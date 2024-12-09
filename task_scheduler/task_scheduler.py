from fastapi import FastAPI, HTTPException
from celery import Celery
import requests

app = FastAPI()

# 配置 Celery
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

MANAGEMENT_API_URL = "https://www.myadmin.com/api"

@app.post("/schedule-task")
def schedule_task(payload: dict):
    """
    调度任务
    """
    instructions = payload.get("instructions", [])
    if not instructions:
        raise HTTPException(status_code=400, detail="No instructions provided")

    task = celery_app.send_task("tasks.execute_task", args=[instructions])
    return {"task_id": task.id}

@celery_app.task(name="tasks.execute_task")
def execute_task(instructions):
    """
    执行任务
    """
    results = []
    for instruction in instructions:
        try:
            # 执行 ADB 操作
            results.append(f"Executed: {instruction}")
        except Exception as e:
            results.append(f"Failed to execute: {str(e)}")
    return results

def fetch_task_status(task_id: str):
    """
    获取任务状态
    """
    try:
        response = requests.get(f"{MANAGEMENT_API_URL}/task-status/{task_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"获取任务状态失败：{e}"}
