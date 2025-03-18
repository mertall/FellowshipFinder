from fastapi import FastAPI, UploadFile, Form
from typing import List
import shutil
import os
import csv
from backend.agent.agent import FellowshipAgent
from backend.storage.storage import save_results, get_results

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/search")
async def search_fellowships(
    university: str = Form(...), 
    field_of_study: str = Form(...), 
    resume: UploadFile = None
):
    # Save resume (optional)
    resume_path = None
    if resume:
        resume_path = f"{UPLOAD_DIR}/{resume.filename}"
        with open(resume_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)

    # Call the agent
    agent = FellowshipAgent()
    results = agent.find_fellowships(university, field_of_study)

    # Save results
    csv_filename = save_results(university, results)
    
    return {"message": "Fellowships found", "csv_file": csv_filename}

@app.get("/results/{university}")
async def get_fellowship_results(university: str):
    return get_results(university)

