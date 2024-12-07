from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

@app.post("/user-input")
def user_input(payload: dict):
    """
    用户输入接口，路由至模型服务
    """
    try:
        model_response = requests.post("http://model_service:8001/process-request", json=payload)
        return model_response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling model service: {str(e)}")

@app.post("/task-status")
def task_status(payload: dict):
    """
    路由任务状态更新至反馈模块
    """
    try:
        feedback_response = requests.post("http://feedback_service:8004/log-feedback", json=payload)
        return feedback_response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling feedback service: {str(e)}")
