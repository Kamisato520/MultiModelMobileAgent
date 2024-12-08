from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟权限验证
async def verify_token(token: str):
    if token != "valid-token":
        raise HTTPException(status_code=401, detail="Invalid token")

@app.middleware("http")
async def authenticate_request(request: Request, call_next):
    token = request.headers.get("Authorization")
    await verify_token(token)
    response = await call_next(request)
    return response

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/route-to-model")
async def route_to_model(payload: dict):
    response = requests.post("http://localhost:8001/process-request", json=payload)
    return JSONResponse(content=response.json())
@app.post("/phone-control/{action}")
async def phone_control(action: str, payload: dict):
    """
    路由请求到手机操作服务
    """
    response = requests.post(f"http://localhost:8002/{action}", json=payload)
    return JSONResponse(content=response.json())
@app.post("/execute-phone-action")
async def execute_phone_action(action: str, payload: dict):
    """
    执行手机操作，并反馈结果
    """
    try:
        adb_response = requests.post(f"http://localhost:8002/{action}", json=payload).json()
        feedback_response = requests.post(
            "http://localhost:8003/record-feedback",
            json={"operation": action, "status": "success", "details": adb_response}
        )
        return {"action_result": adb_response, "feedback": feedback_response.json()}
    except Exception as e:
        requests.post(
            "http://localhost:8003/record-feedback",
            json={"operation": action, "status": "failure", "details": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"Action failed: {str(e)}")
