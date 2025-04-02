import re
import os
import csv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_json_from_string(response: str) -> str:
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if match:
        return match.group(0)
    raise ValueError("No JSON object found in the response.")

def parse_filter_controls(assessment: str):
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

def get_resume_text(resume_path):
    if not os.path.exists(resume_path):
        raise FileNotFoundError(f"Resume not found: {resume_path}")

    with open(resume_path, "r", encoding="utf-8") as f:
        resume_text = f.read()

    if len(resume_text) > 12000:
        print("⚠️ Resume is too long, truncating to fit token limits.")
        resume_text = resume_text[:12000]

    return resume_text

def count_search_results(driver):
    try:
        results = driver.find_elements(By.CSS_SELECTOR, ".search-results .result")
        return len(results)
    except Exception as e:
        print(f"⚠️ Failed to count results: {e}")
        return -1

def extract_table_to_csv(driver, csv_path="fellowship_table_data.csv"):
    try:
        table = WebDriverWait(driver, 5).until(
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

def extract_controls(assessment):
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
