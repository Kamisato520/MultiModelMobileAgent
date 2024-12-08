from fastapi import FastAPI
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
    # 从数据库查询任务指令
    return {"instructions": "click"}

@app.post("/update-task")
def update_task(task: Task):
    # 更新任务状态
    tasks.append(task)
    return {"message": "Task updated successfully"}
