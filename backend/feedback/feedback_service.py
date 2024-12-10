# feedback/feedback_service.py
# 记录和管理任务的反馈信息，如任务执行状态和日志。
# 将反馈信息写入日志文件，便于后续的调试和分析。

import logging
from fastapi import FastAPI, HTTPException

app = FastAPI()

# 配置日志文件
logging.basicConfig(filename="feedback.log", level=logging.INFO)

@app.post("/log-feedback")
def log_feedback(operation: str, status: str, details: str):
    """
    记录任务操作的反馈信息（操作类型、状态、详细信息）
    """
    try:
        log_entry = f"{operation} - {status}: {details}"
        logging.info(log_entry)
        return {"message": "Feedback logged successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"日志记录失败：{str(e)}")
