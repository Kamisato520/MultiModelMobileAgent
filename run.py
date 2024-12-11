# run.py
# 本文件用于启动所有服务，确保各个模块可以正常运行并且相互协作。
# 启动过程中，会初始化所有 FastAPI 服务并运行它们。

import os
import sys
import subprocess
from port import SERVICES
import time
# 将项目根目录添加到 Python 路径
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def start_service(service_name: str):
    """
    启动单个服务
    """
    service = SERVICES.get(service_name)
    if not service:
        print(f"[ERROR] 服务 {service_name} 未找到")
        return 

    host = service["host"]
    port = service["port"]

    # 修正模块路径映射
    module_mapping = {
        "api_gateway": "api_gateway.gateway",
        "model": "model.model_service",
        "phone_control": "phone_control.adb_service",
        "ocr_service": "ocr_service.ocr_service",
        "feedback": "feedback.feedback_service",
        "task_scheduler": "task_scheduler.task_scheduler",
        "cloud_storage": "cloud_storage.storage_service"
    }

    module_path = module_mapping.get(service_name)
    
    if not module_path:
        print(f"[ERROR] 未找到 {service_name} 的模块路径")
        return

    # 调试输出
    print(f"[DEBUG] 模块路径: {module_path}")

    try:
        # 启动服务进程
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", module_path + ":app", "--host", host, "--port", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=backend_dir  # 设置工作目录
        )
                # 超时机制
        start_time = time.time()
        while process.poll() is None:
            if time.time() - start_time > 10:  # 超时时间 10 秒
                process.kill()
                print(f"[ERROR] 服务 {service_name} 启动超时")
                return
            time.sleep(1)
        # 捕获标准输出和错误
        stdout, stderr = process.communicate()
        print(f"[{service_name}] STDOUT: {stdout.decode('utf-8', errors='ignore')}")
        print(f"[{service_name}] STDERR: {stderr.decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"[ERROR] 启动服务 {service_name} 失败：{e}")

if __name__ == "__main__":
    print("[INFO] 启动所有服务...")
    for service_name in SERVICES.keys():
        start_service(service_name)
    print("[INFO] 所有服务已启动")




