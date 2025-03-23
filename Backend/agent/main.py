import time
import re
from lavague.action_engine import ActionEngine
from lavague.world_model import GPTWorldModel
from lavague.agents import WebAgent
from langchain_openai import ChatOpenAI
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class FellowshipSearchAgent:
    """AI agent that automates fellowship searches using LaVague."""

    def __init__(self, use_local_llm=False):
        options = Options()
        options.add_argument("--headless")
        service = Service("/opt/homebrew/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=options)

        if use_local_llm:
            from langchain.llms import HuggingFacePipeline
            from transformers import pipeline
            generator = pipeline("text-generation", model="mistral-7b", device="cuda")
            llm = HuggingFacePipeline(pipeline=generator)
        else:
            llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)

        self.world_model = GPTWorldModel(observations=[])
        self.action_engine = ActionEngine(llm=llm)
        self.agent = WebAgent(driver=self.driver, world_model=self.world_model, action_engine=self.action_engine)
        self.llm = llm

    def assess_search_options(self):
        print("🔍 Assessing page structure...")
        self.agent.get("https://grad.uchicago.edu/fellowships/fellowships-database/")
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
                "Return your response in the following format:\n\n"
                "Thoughts: <bullet point analysis of the webpage layout>\n"
                "Instruction: <single action to perform or STOP if done>\n\n"
                "Objective: Examine webpage — can fellowships be searched or filtered? If yes, determine the tools available (e.g., dropdowns, search fields)\n\n",
                display=True
            )
        finally:
            self.world_model.get_instruction = original_get_instruction

        print(captured_output)
        return captured_output

    def extract_controls(self, assessment):
        filters = []
        for line in assessment.splitlines():
            line = line.strip("-• ").strip()
            if any(keyword in line.lower() for keyword in ["dropdown", "search field", "filter"]):
                match = re.findall(r'"([^"]+)"', line)
                if match:
                    for m in match:
                        canonical = m.strip().title()
                        if canonical not in filters:
                            filters.append(canonical)
        return filters

    def get_user_features(self):
        return {
            "keyword": "machine learning",
            "division": "Physical Sciences",
            "level": "Graduate",
            "deadline": "Spring",
            "type": "Research",
            "eligibility": "International"
        }

    def close(self):
        if self.driver and hasattr(self.driver, 'driver'):
            self.driver.quit()
