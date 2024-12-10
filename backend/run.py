# run.py
# 本文件用于启动所有服务，确保各个模块可以正常运行并且相互协作。
# 启动过程中，会初始化所有 FastAPI 服务并运行它们。

import subprocess
import time
from port import SERVICES

def start_service(service_name: str):
    """
    启动单个服务并捕获输出
    """
    service = SERVICES.get(service_name)
    if not service:
        print(f"[ERROR] 服务 {service_name} 未找到")
        return

    host = service["host"]
    port = service["port"]
    path = f"{service_name.replace('_', '/')}.py"
    print(f"[INFO] 启动 {service_name} 服务，地址：http://{host}:{port}")

    subprocess.Popen(
        ["uvicorn", f"{path}:app", "--host", host, "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

if __name__ == "__main__":
    print("[INFO] 启动所有服务...")
    for service_name in SERVICES.keys():
        start_service(service_name)
    print("[INFO] 所有服务已启动")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] 服务关闭中...")
