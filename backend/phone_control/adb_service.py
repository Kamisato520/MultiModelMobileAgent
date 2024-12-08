import subprocess
from fastapi import FastAPI, HTTPException
import os
import json

app = FastAPI()

# 加载配置
CONFIG_FILE = "config.json"
if not os.path.exists(CONFIG_FILE):
    raise FileNotFoundError("ADB 配置文件未找到，请确保 config.json 存在。")

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

adb_path = config.get("adb_path", "adb")

def run_adb_command(command):
    """
    通用 ADB 命令执行函数
    """
    try:
        full_command = f"{adb_path} {command}"
        result = subprocess.check_output(full_command, shell=True, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"ADB 命令执行失败: {e.output}")

@app.post("/connect-device")
def connect_device(device_ip: str):
    result = run_adb_command(f"connect {device_ip}")
    return {"message": result}

@app.post("/install-app")
def install_app(apk_path: str):
    if not os.path.exists(apk_path):
        raise HTTPException(status_code=400, detail="APK 文件不存在")
    result = run_adb_command(f"install {apk_path}")
    return {"message": result}

@app.post("/send-key-event")
def send_key_event(key_code: int):
    result = run_adb_command(f"shell input keyevent {key_code}")
    return {"message": result}

@app.post("/swipe-screen")
def swipe_screen(x1: int, y1: int, x2: int, y2: int, duration: int = 100):
    result = run_adb_command(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")
    return {"message": result}

@app.post("/input-text")
def input_text(text: str):
    sanitized_text = text.replace(" ", "%s")
    result = run_adb_command(f"shell input text {sanitized_text}")
    return {"message": result}
