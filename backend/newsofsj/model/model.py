import openai
import json
from fastapi import FastAPI, HTTPException

# 加载配置
with open("config.json", "r") as f:
    config = json.load(f)

openai.api_key = config["api_key"]

app = FastAPI()

# @app.post("/process-request")
# async def process_request(request: dict):
#     try:
#         user_input = request.get("input")
#         model_name = config.get("model_name", "gpt-4")
#         response = openai.Completion.create(
#             model=model_name,
#             prompt=user_input,
#             max_tokens=150
#         )
#         return {"response": response.choices[0].text.strip()}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-request")
def process_request(payload: dict):
    """
    处理用户输入，并生成指令
    """
    user_input = payload.get("user_input", "")
    screenshot = payload.get("screenshot", None)  # 获取截屏内容

    try:
        prompt = f"用户请求: {user_input}\n截屏内容: {screenshot}\n请生成手机操作指令:"
        response = openai.Completion.create(
            model=config["model_name"],
            prompt=prompt,
            max_tokens=150
        )
        return {"instructions": response.choices[0].text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model API Error: {str(e)}")
