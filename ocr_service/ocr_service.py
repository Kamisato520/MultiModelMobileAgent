# ocr_service/ocr_service.py
# 该文件负责接收图片 URL，调用 OCR 模型（qwen-vl-ocr）进行文字识别。
# 处理完的 OCR 结果将返回给调用方，供大模型进一步处理。

import json
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from port import get_service_url

app = FastAPI()

# 加载配置文件
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except Exception as e:
    raise RuntimeError(f"配置文件加载失败：{e}")

try:
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
except Exception as e:
    raise RuntimeError(f"OpenAI 客户端初始化失败：{e}")

@app.post("/process-image")
def process_image(payload: dict):
    """
    接收图片 URL，调用 OCR 模型进行文字识别。
    返回从图片中提取的文字内容。
    """
    image_url = payload.get("image_url")
    if not image_url:
        raise HTTPException(status_code=400, detail="缺少图片 URL")

    try:
        response = client.chat.completions.create(
            model=config["model_name"],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": image_url},
                        {"type": "text", "text": "提取图片中的所有文字"}
                    ]
                }
            ],
            max_tokens=2000,
            top_p=0.01,
            temperature=0.1
        )
        return {"ocr_text": response.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR 调用失败：{e}")
