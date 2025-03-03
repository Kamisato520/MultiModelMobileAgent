class AutomationError(Exception):
    """自动化相关错误的基类"""
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code

class DeviceError(AutomationError):
    """设备相关错误"""
    pass

class TaskError(AutomationError):
    """任务相关错误"""
    pass

class LLMError(AutomationError):
    """LLM服务相关错误"""
    pass

class WebSocketError(AutomationError):
    """WebSocket相关错误"""
    pass

def format_error_response(error):
    """格式化错误响应"""
    return {
        'error': {
            'type': error.__class__.__name__,
            'message': str(error),
            'code': getattr(error, 'error_code', None)
        }
    } 