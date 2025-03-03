# backend/app/config.py
import os
import secrets
from datetime import timedelta

class Config:
    # 生成安全的随机密钥
    SECRET_KEY = secrets.token_hex(24)
    
    # 数据库连接URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///automation.db'  # 可以根据需要修改数据库类型和位置
    
    # SQLAlchemy设置
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 建议保持False以提高性能
    
    # 阿里云百炼API配置（已提供）
    DASHSCOPE_API_KEY = 'sk-4a6e5901c20f43139c2c84d8e9bd50f2'
    
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

    # 安全相关配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret'
    
    # 会话配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000']  # 允许的前端域名
    
    # 密码策略
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL_CHARS = True

# 生产环境配置
class ProductionConfig(Config):
    # 使用环境变量或更安全的配置管理系统
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(24)
    
    # 生产环境数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://root:123456@localhost/automation_prod'

# 开发环境配置
class DevelopmentConfig(Config):
    DEBUG = True
