from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# 假设数据库连接已完成
tasks = []

class Task(BaseModel):
    task_id: str
    status: str
    details: dict

@app.get("/get-instructions")
def get_instructions():
    """
    从数据库查询任务指令
    """
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found")
    # 假设返回一个任务指令
    return {"instructions": tasks[-1]["details"].get("instructions", "No instructions available")}

@app.post("/update-task")
def update_task(task: Task):
    """
    更新任务状态
    """
    tasks.append(task.dict())
    return {"message": "Task updated successfully", "task_id": task.task_id}
