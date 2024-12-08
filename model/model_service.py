import requests
import json
from fastapi import FastAPI, HTTPException
import os
app = FastAPI()

# 加载配置
with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
    config = json.load(f)

# with open("config.json", "r") as f:
#     config = json.load(f)

api_key = config["api_key"]
api_url = config["api_url"]
model_name = config["model_name"]

@app.post("/process-request")
def process_request(payload: dict):
    """
    根据用户输入与截屏生成手机操作指令
    """
    user_input = payload.get("user_input", "")
    screenshot_description = payload.get("screenshot_description", "未提供截屏描述")  # 截屏的文字描述

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model_name,
        "prompt": f"用户请求: {user_input}\n当前截屏信息: {screenshot_description}\n请生成具体的手机操作指令：",
        "max_tokens": 150
    }

    try:
        # 调用 Qwen-Plus 模型 API
        response = requests.post(api_url, headers=headers, json=data)
        response_data = response.json()

        if response.status_code == 200:
            return {"instructions": response_data["choices"][0]["text"].strip()}
        else:
            raise HTTPException(status_code=response.status_code, detail="Error from model service")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model API Error: {str(e)}")
    """
    调用 OCR 和大模型生成响应
    """
    image_url = payload.get("image_url", None)
    user_input = payload.get("user_input", "")
    system_prompt = payload.get("system_prompt", "You are a helpful assistant.")

    # 调用 OCR 服务
    ocr_text = ""
    if image_url:
        try:
            ocr_response = requests.post("https://dashscope.aliyuncs.com/compatible-mode/v1", json={"image_url": image_url})
            ocr_response.raise_for_status()
            ocr_text = ocr_response.json().get("ocr_text", "")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"OCR 服务调用失败：{e}")

    try:
        # 调用大模型
        response = client.chat.completions.create(
            model=config["model_name"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{user_input}\nOCR 内容: {ocr_text}"}
            ]
        )
        return {"response": response.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型调用失败：{e}")