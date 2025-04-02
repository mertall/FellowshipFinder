import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import csv
import os

from fastapi.responses import FileResponse

from Backend.agent.agent import FellowshipSearchAgent

app = FastAPI()

# ✅ Allow requests from frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Update with frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

CSV_FILE = "Backend/common/universities.csv"

@app.get("/universities")
async def get_universities():
    """Fetches the list of universities and their fellowship links."""
    
    universities = _get_universities()
    return {"universities": universities}

@app.get("/fellowships")
async def get_fellowships():
    """Fetches the CSV of fellowships based on user's resume."""
    universities = _get_universities()
    urls=_get_university_links_only(universities)
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        futures = [
            loop.run_in_executor(executor, lambda url=u: _run_single_agent(url))
            for u in urls
        ]
        await asyncio.gather(*futures)

def _get_universities():
    if not os.path.exists(CSV_FILE):
        return {"error": "University list not found."}

    universities = []
    with open(CSV_FILE, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            universities.append({"name": row["University"], "link": row["Link"]})
    return universities

def _get_university_links_only(raw):
    if isinstance(raw, dict) and "error" in raw:
        return []
    return [entry["link"] for entry in raw if "link" in entry]

def _run_single_agent(url):
        agent = FellowshipSearchAgent()
        try:
            agent.run_workflow(url=url)
        finally:
            agent.close()
