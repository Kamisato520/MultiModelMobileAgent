# backend/app/config.py
class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///automation.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 阿里云百炼API配置
    DASHSCOPE_API_KEY = 'your-dashscope-api-key'
    
    # 模型配置
    MODELS = {
        'text': {
            'name': 'qwen-plus',
            'api_url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation'
        },
        'vision': {
            'name': 'qwen-vl-max',
            'api_url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'
        },
        'ocr': {
            'name': 'qwen-vl-ocr',
            'api_url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'
        },
        'audio': {
            'name': 'qwen-audio-turbo',
            'api_url': 'https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation'
        }
    }
    
    WEBSOCKET_PORT = 8765