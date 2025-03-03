from functools import wraps
from flask_caching import Cache
from app import app

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': app.config['REDIS_URL'],
    'CACHE_DEFAULT_TIMEOUT': 300
})

def cache_llm_response(timeout=300):
    """LLM响应缓存装饰器"""
    def decorator(f):
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            # 生成缓存键
            cache_key = f"llm:{f.__name__}:{str(args)}:{str(kwargs)}"
            
            # 尝试从缓存获取
            response = cache.get(cache_key)
            if response is not None:
                return response
                
            # 执行原函数
            response = await f(*args, **kwargs)
            
            # 存入缓存
            cache.set(cache_key, response, timeout=timeout)
            return response
        return decorated_function
    return decorator 