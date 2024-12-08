import json
from fastapi import FastAPI, HTTPException
from openai import OpenAI

app = FastAPI()

# 加载配置
with open("config.json", "r") as f:
    config = json.load(f)

# 初始化 OpenAI 客户端
try:
    client = OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )
except Exception as e:
    raise RuntimeError(f"初始化 OpenAI 客户端失败：{e}")

@app.post("/process-image")
def process_image(payload: dict):
    """
    调用 qwen-vl-ocr 模型进行 OCR 识别
    """
    image_url = payload.get("image_url", None)
    if not image_url:
        raise HTTPException(status_code=400, detail="必须提供图片 URL")

    try:
        # 调用 qwen-vl-ocr 模型
        response = client.chat.completions.create(
            model=config["model_name"],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": image_url,
                            "min_pixels": 28 * 28 * 4,
                            "max_pixels": 1280 * 784
                        },
                        {"type": "text", "text": "Read all the text in the image."}
                    ]
                }
            ],
            top_p=0.01,
            temperature=0.1,
            max_tokens=2000
        )
        return {"ocr_text": response.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR 调用失败：{e}")
