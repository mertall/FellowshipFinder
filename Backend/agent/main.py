import csv
from concurrent.futures import ThreadPoolExecutor
import time
import re
import os
import json
from lavague.action_engine import ActionEngine
from lavague.world_model import GPTWorldModel
from lavague.agents import WebAgent
from langchain_openai import ChatOpenAI
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FellowshipSearchAgent:
    """AI agent that automates fellowship searches using LaVague and LangChain."""

    def __init__(self, use_local_llm=False):
        options = Options()
        #options.add_argument("--headless")
        service = Service("/opt/homebrew/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=options)

        if use_local_llm:
            from langchain.llms import HuggingFacePipeline
            from transformers import pipeline
            generator = pipeline("text-generation", model="mistral-7b", device="cuda")
            llm = HuggingFacePipeline(pipeline=generator)
        else:
            llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.3, max_tokens=1024)

        self.llm = llm
        self.world_model = GPTWorldModel(observations=[])
        self.action_engine = ActionEngine(llm=llm)
        self.agent = WebAgent(driver=self.driver, world_model=self.world_model, action_engine=self.action_engine)

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

    def assess_search_options(self, link = "https://grad.uchicago.edu/fellowships/fellowships-database/"):
        print("Assessing page structure...")
        self.agent.get(link)
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

    def extract_controls(self, assessment):
        filters = []
        for line in assessment.splitlines():
            line = line.strip("-• ").strip()
            if any(k in line.lower() for k in ["dropdown", "search field", "filter", "button"]):
                match = re.findall(r'"([^"]+)"', line)
                for m in match:
                    canonical = m.strip().title()
                    if canonical not in filters:
                        filters.append(canonical)
        return filters
    def extract_json_from_string(self, response: str) -> str:
        """Extract the JSON object from a string using regex."""
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return match.group(0)
        else:
            raise ValueError("No JSON object found in the response.")
        
    def get_user_features(self, controls, resume_path="Backend/common/resume.txt"):
        if not os.path.exists(resume_path):
            raise FileNotFoundError(f"Resume not found: {resume_path}")

        with open(resume_path, "r", encoding="utf-8") as f:
            resume_text = f.read()

        if len(resume_text) > 12000:
            print("⚠️ Resume is too long, truncating to fit token limits.")
            resume_text = resume_text[:12000]

        prompt = PromptTemplate.from_template("""
        You are helping a student apply for fellowships. Based on the resume below, assign values to the following filters:

        Filters:
        {controls}

        Resume:
        ---
        {resume_text}
        ---

        Return a valid JSON object with these keys.
        """)

        try:
            chain = RunnableLambda(lambda _: {"resume_text": resume_text, "controls": controls}) | prompt | self.llm | StrOutputParser()
            response = chain.invoke({})
            print(response)
            parsed = json.loads(self.extract_json_from_string(response))

            return parsed
        except Exception as e:
            print(f"⚠️ Could not parse features: {e}\n")
            return {
                "Keyword": "machine learning",
                "Division": "Physical Sciences",
                "Level": "Graduate",
                "Deadline": "Spring",
                "Type": "Research",
                "Eligibility": "International"
            }

    def count_search_results(self):
        try:
            results = self.driver.find_elements(By.CSS_SELECTOR, ".search-results .result")
            return len(results)
        except Exception as e:
            print(f"⚠️ Failed to count results: {e}")
            return -1


    def extract_table_to_csv(self, csv_path="fellowship_table_data.csv"):
        try:
            table = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )

            rows = table.find_elements(By.TAG_NAME, "tr")
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                for row in rows:
                    cols = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
                    writer.writerow([col.text.strip() for col in cols])

            print(f"✅ Table data exported to {csv_path}")
        except Exception as e:
            print(f"⚠️ Failed to extract table to CSV: {e}")

    def run_workflow(self):
        self.agent.get("https://grad.uchicago.edu/fellowships/fellowships-database/")
        time.sleep(2)
        initial_results = self.count_search_results()
        print(f"🔢 Initial number of results: {initial_results}")

        assessment = self.assess_search_options()
        controls = self.extract_controls(assessment)
        print("✅ Detected Controls:", controls)

        features = self.get_user_features(controls)

        mapping_prompt = PromptTemplate.from_template("""
        You an AI Agent tasked to find the best fellowships by interacting with a fellowships page instead of the user:

        The following UI controls were detected on the fellowship search page:
        {controls}

        The following user preferences were extracted:
        {features}

         Create 1 instruction to apply a user preference to a UI control. Only create instructions if it will truly benefit the student in finding a fellowship for them.
        The instruction should guide an AI agent how to:
        - Interact with the control for that field (click/select/search text box)
        - Apply the users filter value appropriately, text entry, selecting checkbox(es)
        - Ensure selection or visual confirmation, do not revert a change by accident
                                                      
                

        Return a list of short, clear action steps to be executed by the agent for what you deem as beneficial to narrowing down fellowships for a student.
        - Remove all but 10 most crucial steps to complete. Filter now.
        - Append a final instruction for executing, filtering, searching, or some synonymous action on the web page based on controls given. ALWAYS the last instruction. Reorder instructions to make sure this is the case.
        - "Return your response as list of the following the format:\n\n"
            "Thoughts: <Full instructions> \n"
            "Instruction: <Instruction core steps or STOP if it is completed>\n\n"
            "Objective: <General goal of intstruction>
        """)

        planner = (
            RunnableLambda(lambda _: {"controls": ", ".join(controls), "features": features})
            | mapping_prompt
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
        final_results = self.count_search_results()
        print(f"🔢 Final number of results: {final_results}")
        self.extract_table_to_csv()
        
    def close(self):
        if self.driver and hasattr(self.driver, 'quit'):
            self.driver.quit()
