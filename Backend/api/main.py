from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import csv
import os

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
    if not os.path.exists(CSV_FILE):
        return {"error": "University list not found."}

    universities = []
    with open(CSV_FILE, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            universities.append({"name": row["University"], "link": row["Link"]})

    return {"universities": universities}
