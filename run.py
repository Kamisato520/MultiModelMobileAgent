# run.py
# 本文件用于启动所有服务，确保各个模块可以正常运行并且相互协作。
# 启动过程中，会初始化所有 FastAPI 服务并运行它们。

import subprocess
import time
import os

# 模块服务的配置信息
services = {
    "api_gateway": {"port": 8000, "path": "api_gateway/gateway.py"},
    "model_service": {"port": 8001, "path": "model/model_service.py"},
    "phone_control": {"port": 8002, "path": "phone_control/adb_service.py"},
    "ocr_service": {"port": 8006, "path": "ocr_service/ocr_service.py"},
}

def start_service(name, config):
    """
    启动单个服务并捕获输出
    """
    try:
        print(f"[INFO] Starting {name} on port {config['port']}...")
        subprocess.Popen(
            ["uvicorn", f"{config['path']}:app", "--host", "127.0.0.1", "--port", str(config['port'])],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except Exception as e:
        print(f"[ERROR] 启动服务 {name} 失败：{e}")

if __name__ == "__main__":
    print("[INFO] 启动所有服务...")
    for name, config in services.items():
        start_service(name, config)
    print("[INFO] 所有服务已启动")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] 服务关闭中...")
