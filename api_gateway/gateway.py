from fastapi import FastAPI, HTTPException
import requests

# 确保有 app 定义
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API Gateway is running"}

@app.post("/user-input")
def user_input(payload: dict):
    try:
        # 路由到模型服务
        model_response = requests.post("http://model_service:8001/process-request", json=payload)
        return model_response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling model service: {str(e)}")
    """
    转发用户请求到模型服务
    """
    try:
        model_response = requests.post("http://localhost:8001/process-request", json=payload)
        model_response.raise_for_status()
        return model_response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"模型服务调用失败：{e}")
@app.post("/task-status")
def task_status(payload: dict):
    try:
        # 反馈任务状态
        feedback_response = requests.post("http://feedback_service:8004/log-feedback", json=payload)
        return feedback_response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling feedback service: {str(e)}")
