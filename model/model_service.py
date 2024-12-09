# model/model_service.py
# 本文件处理来自 API 网关的请求，调用云端大模型（如 qwen-plus）并返回指令。
# 也处理OCR服务调用的集成，生成与用户请求相关的手机操作指令。

import requests
import json
from fastapi import FastAPI, HTTPException
import os

app = FastAPI()

# 加载配置文件
try:
    with open(os.path.join(os.path.dirname(__file__), "config.json"), "r") as f:
        config = json.load(f)
except Exception as e:
    raise RuntimeError(f"配置文件加载失败：{e}")

api_key = config["api_key"]
api_url = config["api_url"]
model_name = config["model_name"]

@app.post("/process-request")
def process_request(payload: dict):
    """
    根据用户输入和截屏内容生成手机操作指令。
    如果包含图片URL，先调用 OCR 获取图片中的文字信息，再交给大模型生成指令。
    """
    user_input = payload.get("user_input", "")
    screenshot_url = payload.get("image_url", None)

    # 发送 OCR 请求
    ocr_text = ""
    if screenshot_url:
        try:
            ocr_response = requests.post(
                "http://localhost:8006/process-image",
                json={"image_url": screenshot_url}
            )
            ocr_response.raise_for_status()
            ocr_text = ocr_response.json().get("ocr_text", "")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"OCR 服务调用失败：{e}")

    # 调用大模型服务
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model_name,
        "prompt": f"用户请求: {user_input}\nOCR 结果: {ocr_text}",
        "max_tokens": 150
    }

    try:
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        return {"instructions": response.json().get("choices", [{}])[0].get("text", "").strip()}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"模型调用失败：{e}")
