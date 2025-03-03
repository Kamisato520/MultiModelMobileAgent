import time
from functools import wraps
from app.utils.logger import logger
from prometheus_client import Counter, Histogram

# 定义指标
request_count = Counter('http_requests_total', 'Total HTTP requests')
request_latency = Histogram('http_request_latency_seconds', 'HTTP request latency')
llm_request_count = Counter('llm_requests_total', 'Total LLM API calls')
llm_request_latency = Histogram('llm_request_latency_seconds', 'LLM API latency')

def monitor_performance(f):
    """性能监控装饰器"""
    @wraps(f)
    async def wrapped(*args, **kwargs):
        request_count.inc()
        start_time = time.time()
        
        try:
            result = await f(*args, **kwargs)
            return result
        finally:
            latency = time.time() - start_time
            request_latency.observe(latency)
            
            if latency > 1.0:  # 记录慢请求
                logger.warning(f"Slow request detected: {f.__name__} took {latency:.2f}s")
                
    return wrapped

def monitor_llm_call(f):
    """LLM调用监控装饰器"""
    @wraps(f)
    async def wrapped(*args, **kwargs):
        llm_request_count.inc()
        start_time = time.time()
        
        try:
            result = await f(*args, **kwargs)
            return result
        finally:
            latency = time.time() - start_time
            llm_request_latency.observe(latency)
            
            if latency > 5.0:  # 记录慢LLM调用
                logger.warning(f"Slow LLM call detected: {latency:.2f}s")
                
    return wrapped 