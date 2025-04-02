import time
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from lavague.action_engine import ActionEngine
from lavague.world_model import GPTWorldModel
from lavague.agents import WebAgent
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from Backend.agent.prompts import get_filter_prompt, get_action_plan_prompt
from Backend.agent.utils import extract_json_from_string, parse_filter_controls, count_search_results, extract_table_to_csv

class FellowshipSearchAgent:
    def __init__(self, use_local_llm=False):
        options = Options()
        # options.add_argument("--headless")
        service = Service("/opt/homebrew/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=options)

        self.llm = self._load_llm(use_local_llm)
        self.world_model = GPTWorldModel(observations=[])
        self.action_engine = ActionEngine(llm=self.llm)
        self.agent = WebAgent(driver=self.driver, world_model=self.world_model, action_engine=self.action_engine)

    def _load_llm(self, use_local):
        if use_local:
            from langchain.llms import HuggingFacePipeline
            from transformers import pipeline
            generator = pipeline("text-generation", model="mistral-7b", device="cuda")
            return HuggingFacePipeline(pipeline=generator)
        return ChatOpenAI(model="gpt-4-turbo", temperature=0.3, max_tokens=1024)

    def safe_agent_run(self, prompt: str, step_label: str = "", retries: int = 0):
        attempt = 0
        while attempt <= retries:
            try:
                print(f"Starting step: {step_label} (attempt {attempt + 1})")
                return self.agent.run(prompt, display=True)
            except ValueError as ve:
                if "No instruction found" in str(ve):
                    print(f"Step '{step_label}' attempt {attempt + 1}: No instruction returned.")
                    attempt += 1
                    if attempt > retries:
                        print(f"Step '{step_label}' skipped after {retries + 1} attempts.")
                else:
                    raise
            except Exception as e:
                print(f"Step '{step_label}' failed: {e}")
                break

    def assess_search_options(self, url):
        if url is None:
            url ="https://grad.uchicago.edu/fellowships/fellowships-database/"
        print("Assessing page structure...")
        self.agent.get(url)
        time.sleep(3)

        captured_output = None
        original_get_instruction = self.world_model.get_instruction

        def get_instruction_patch(state, objective):
            nonlocal captured_output
            output = original_get_instruction(state, objective)
            captured_output = output
            return output

        self.world_model.get_instruction = get_instruction_patch

        try:
            self.agent.run(
                "Return your response in the format:\n\n"
                "Thoughts: <bullet points>\n"
                "Instruction: <single step or STOP>\n\n"
                "Objective: Determine if the fellowships can be searched or filtered. If so, identify the filtering tools (e.g., dropdowns, search fields).",
                display=True
            )
        finally:
            self.world_model.get_instruction = original_get_instruction

        print(captured_output)
        return captured_output

    def get_user_features(self, controls, resume_path="Backend/common/resume.txt"):
        if not os.path.exists(resume_path):
            raise FileNotFoundError(f"Resume not found: {resume_path}")

        with open(resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()
        if len(resume_text) > 12000:
            print("⚠️ Resume is too long, truncating to fit token limits.")
            resume_text = resume_text[:12000]

        prompt = get_filter_prompt()

        try:
            chain = RunnableLambda(lambda _: {"resume_text": resume_text, "controls": controls}) | prompt | self.llm | StrOutputParser()
            response = chain.invoke({})
            return json.loads(extract_json_from_string(response))
        except Exception as e:
            print(f"⚠️ Could not parse features: {e}\n")
            return {}

    def run_workflow(self, url=None):

        assessment = self.assess_search_options(url)
        controls = parse_filter_controls(assessment)
        print("✅ Detected Controls:", controls)

        features = self.get_user_features(controls)

        planner = (
            RunnableLambda(lambda _: {"controls": ", ".join(controls), "features": features})
            | get_action_plan_prompt()
            | self.llm
            | StrOutputParser()
        )

        try:
            action_plan = planner.invoke({}).split("\n")
        except Exception as e:
            print(f"⚠️ Failed to create dynamic action plan: {e}")
            return

        for i, step in enumerate(action_plan):
            if step.strip():
                self.safe_agent_run(step, step_label=f"Dynamic Step {i+1}")

        time.sleep(3)
        extract_table_to_csv(self.driver)

    def close(self):
        if self.driver and hasattr(self.driver, 'quit'):
            self.driver.quit()


