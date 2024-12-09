# api_gateway/gateway.py
# 本文件作为 API 网关，负责接收用户请求并转发至模型服务、反馈服务等。
# 实现了与大模型和任务管理相关的接口，确保各模块间的通信顺畅。

from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

# 模型服务地址
MODEL_SERVICE_URL = "https://www.myexample.com/api"

@app.get("/")
def read_root():
    """
    根路由，确认 API 网关是否运行正常
    """
    return {"message": "API Gateway is running"}

@app.post("/user-input")
def user_input(payload: dict):
    """
    接收用户输入，转发至大模型服务进行处理，并返回大模型响应
    """
    try:
        response = requests.post(f"{MODEL_SERVICE_URL}/process-request", json=payload)
        response.raise_for_status()
        return {"data": response.json()}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="调用大模型失败")

@app.post("/task-status")
def task_status(payload: dict):
    """
    接收任务状态更新，转发至反馈服务记录任务状态
    """
    try:
        response = requests.post("http://localhost:8004/log-feedback", json=payload)
        response.raise_for_status()
        return {"data": response.json()}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="调用反馈服务失败")
