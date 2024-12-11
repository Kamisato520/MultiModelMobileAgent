from fastapi import FastAPI, HTTPException
from celery import Celery
import requests
from port import get_service_url  # 从 port.py 引入获取服务 URL 的函数

app = FastAPI()

# 配置 Celery
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# 获取管理 API 服务 URL
MANAGEMENT_API_URL = get_service_url("task_scheduler")
@app.get("/")
def read_root():
    """
    根路径，用于确认服务是否正常运行。
    """
    
    return {"message": "Task Manager Service is running"}
@app.post("/schedule-task")
def schedule_task(payload: dict):
    """
    调度任务，接收用户请求，执行后台任务，并返回任务 ID。
    """
    instructions = payload.get("instructions", [])
    if not instructions:
        raise HTTPException(status_code=400, detail="No instructions provided")

    task = celery_app.send_task("tasks.execute_task", args=[instructions])
    return {"task_id": task.id}

@celery_app.task(name="tasks.execute_task")
def execute_task(instructions):
    """
    执行任务，按照给定的指令执行相应操作（例如 ADB 操作）。
    """
    results = []
    for instruction in instructions:
        try:
            # 执行 ADB 操作
            # 示例代码：在实际环境中，应该调用 adb_service 进行操作
            results.append(f"Executed: {instruction}")
        except Exception as e:
            results.append(f"Failed to execute: {str(e)}")
    return results

def fetch_task_status(task_id: str):
    """
    获取任务状态，查询任务在管理系统中的执行状态。
    """
    try:
        response = requests.get(f"{MANAGEMENT_API_URL}/task-status/{task_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"获取任务状态失败：{e}"}
