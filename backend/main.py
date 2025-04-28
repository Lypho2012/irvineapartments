"""
Start server by running fastapi dev main.py
Activate venv with source ./.venv/bin/activate
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scraper import get_latest_movein, gmail_send_message

import json

app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/get-today-report")
async def getTodayReport():
    getTodayReport_aux()

def getTodayReport_aux():
    print("Sending email...")
    
    plans = {}
    with open("plans.json","r") as file:
        plans = json.load(file)
    
    message = ""
    for plan in plans.keys():
        message += plan + ": " + get_latest_movein(plans[plan]["url"],plans[plan]["name"]) + "\n"

    print(message)
    gmail_send_message(message)
    print("Email sent")

if __name__ == "__main__":
    getTodayReport_aux()