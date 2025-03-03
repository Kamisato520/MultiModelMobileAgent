from functools import wraps
from flask import request, jsonify
from flask_login import current_user
import jwt
from datetime import datetime, timedelta
from app.config import Config
from app.models.user import User
from app.utils.logger import logger

def generate_token(user):
    """生成JWT令牌"""
    payload = {
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return User.query.get(payload['user_id'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_api_key(f):
    """API密钥验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key is missing'}), 401

        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401

        return f(*args, **kwargs)
    return decorated

def require_admin(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated

def verify_websocket_token(token):
    """验证WebSocket连接令牌"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        user = User.query.get(payload['user_id'])
        if user and user.is_active:
            return user
        return None
    except Exception as e:
        logger.error(f"WebSocket token verification failed: {str(e)}")
        return None 