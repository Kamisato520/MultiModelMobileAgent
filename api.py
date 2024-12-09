import os
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL", "http://localhost:8001")

@app.post("/route-to-model")
async def route_to_model(payload: dict):
    response = requests.post(f"{MODEL_SERVICE_URL}/process-request", json=payload)
    response.raise_for_status()
    return response.json()
