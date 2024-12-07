import logging
from fastapi import FastAPI

app = FastAPI()

logging.basicConfig(filename="feedback.log", level=logging.INFO)

@app.post("/log-feedback")
def log_feedback(operation: str, status: str, details: str):
    log_entry = f"{operation} - {status}: {details}"
    logging.info(log_entry)
    return {"message": "Feedback logged"}
