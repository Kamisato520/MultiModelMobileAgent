import subprocess
from fastapi import FastAPI, HTTPException
import os
import json

# 初始化 FastAPI 应用
app = FastAPI()

# 配置文件路径
CONFIG_FILE = "config.json"

# 检查 ADB 工具是否可用
if not os.path.exists("adb"):
    raise FileNotFoundError("ADB工具未找到，请确保ADB工具在路径中或指定路径。")

# 加载配置
def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

config = load_config()
adb_path = config.get("adb_path", "adb")

# 通用ADB命令执行函数
def run_adb_command(command):
    try:
        full_command = f"{adb_path} {command}"
        result = subprocess.check_output(full_command, shell=True, text=True)
        return result.strip()
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"ADB命令执行失败: {e.output}")

# FastAPI 路由
@app.post("/connect-device")
def connect_device(device_ip: str):
    """
    连接指定设备
    """
    result = run_adb_command(f"connect {device_ip}")
    return {"message": result}

@app.post("/install-app")
def install_app(apk_path: str):
    """
    安装APK到设备
    """
    if not os.path.exists(apk_path):
        raise HTTPException(status_code=400, detail="APK文件不存在")
    result = run_adb_command(f"install {apk_path}")
    return {"message": result}

@app.post("/send-key-event")
def send_key_event(key_code: int):
    """
    模拟按键事件
    """
    result = run_adb_command(f"shell input keyevent {key_code}")
    return {"message": result}

@app.post("/swipe-screen")
def swipe_screen(x1: int, y1: int, x2: int, y2: int, duration: int = 100):
    """
    模拟滑动屏幕
    """
    result = run_adb_command(f"shell input swipe {x1} {y1} {x2} {y2} {duration}")
    return {"message": result}

@app.post("/input-text")
def input_text(text: str):
    """
    模拟输入文字
    """
    sanitized_text = text.replace(" ", "%s")  # 替换空格
    result = run_adb_command(f"shell input text {sanitized_text}")
    return {"message": result}
