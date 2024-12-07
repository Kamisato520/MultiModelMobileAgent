import subprocess
import time
import os

# 模块服务的配置信息
services = {
    "api_gateway": {"port": 8000, "path": "api_gateway/gateway.py"},
    "model_service": {"port": 8001, "path": "model/model_service.py"},
    "phone_control": {"port": 8002, "path": "phone_control/adb_service.py"},
    "task_manager": {"port": 8003, "path": "task_manager/task_scheduler.py"},
    "feedback_service": {"port": 8004, "path": "feedback/feedback_service.py"},
    "cloud_storage": {"port": 8005, "path": "cloud_storage/storage_service.py"},
}

# 启动单个服务
def start_service(name, config):
    port = config["port"]
    path = config["path"]

    print(f"[INFO] Starting {name} on port {port}...")
    subprocess.Popen(
        ["uvicorn", path + ":app", "--host", "127.0.0.1", "--port", str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


# 启动所有服务
def start_all_services():
    for name, config in services.items():
        start_service(name, config)


# 主函数
if __name__ == "__main__":
    print("[INFO] Starting all services...")
    start_all_services()
    print("[INFO] All services started. Press Ctrl+C to stop.")

    # 持续运行以保持主进程
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down all services...")
