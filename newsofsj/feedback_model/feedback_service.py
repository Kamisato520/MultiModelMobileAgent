from fastapi import FastAPI, HTTPException
import logging
from datetime import datetime

# 初始化日志
logging.basicConfig(
    filename="feedback.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = FastAPI()

@app.post("/record-feedback")
def record_feedback(operation: str, status: str, details: str = ""):
    """
    记录操作结果和反馈信息
    """
    if status not in ["success", "failure"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    feedback = {
        "timestamp": datetime.now().isoformat(),
        "operation": operation,
        "status": status,
        "details": details
    }

    # 记录到日志文件
    logging.info(f"Feedback: {feedback}")
    return {"message": "Feedback recorded", "feedback": feedback}

@app.get("/get-feedback-log")
def get_feedback_log():
    """
    返回反馈日志
    """
    try:
        with open("feedback.log", "r") as log_file:
            logs = log_file.readlines()
        return {"logs": logs}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Feedback log not found")
