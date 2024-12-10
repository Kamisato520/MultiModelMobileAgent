# port.py
"""
管理后端所有服务的端口和相关配置信息。
此文件用于集中存储服务的端口信息，便于维护和全局调用。
"""

# 服务端口配置
SERVICES = {
    "api_gateway": {
        "host": "127.0.0.1",
        "port": 8000,
        "description": "API 网关，用于处理前端请求并协调后端服务"
    },
    "model_service": {
        "host": "127.0.0.1",
        "port": 8001,
        "description": "模型服务，用于调用大模型生成响应指令"
    },
    "phone_control": {
        "host": "127.0.0.1",
        "port": 8002,
        "description": "手机控制服务，用于执行 ADB 操作"
    },
    "ocr_service": {
        "host": "127.0.0.1",
        "port": 8006,
        "description": "OCR 服务，用于图片文字识别"
    },
    "feedback_service": {
        "host": "127.0.0.1",
        "port": 8004,
        "description": "反馈服务，用于记录任务的执行反馈"
    },
    "task_manager": {
        "host": "127.0.0.1",
        "port": 8003,
        "description": "任务管理服务，用于处理任务的调度和状态管理"
    },
    "cloud_storage": {
        "host": "127.0.0.1",
        "port": 8005,
        "description": "云存储服务，用于文件上传和下载"
    }
}

# 获取服务地址
def get_service_url(service_name: str) -> str:
    """
    根据服务名称返回对应的 URL。
    :param service_name: 服务名称（如 'api_gateway', 'model_service'）
    :return: 完整的服务 URL
    """
    service = SERVICES.get(service_name)
    if not service:
        raise ValueError(f"服务 {service_name} 未找到，请检查配置")
    return f"http://{service['host']}:{service['port']}"

# 示例：获取 API 网关的 URL
if __name__ == "__main__":
    print(get_service_url("api_gateway"))  # 输出：http://127.0.0.1:8000
