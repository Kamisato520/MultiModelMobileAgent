import logging
import logging.handlers
import os
from datetime import datetime

class CustomFormatter(logging.Formatter):
    """自定义日志格式化器"""
    
    def format(self, record):
        if hasattr(record, 'task_id'):
            record.task_id_str = f'[Task:{record.task_id}]'
        else:
            record.task_id_str = ''
            
        if hasattr(record, 'device_id'):
            record.device_id_str = f'[Device:{record.device_id}]'
        else:
            record.device_id_str = ''
            
        return super().format(record)

def setup_logger():
    """配置日志系统"""
    
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(__file__), '../../logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # 获取根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # 日志格式
    formatter = CustomFormatter(
        '%(asctime)s %(levelname)s %(task_id_str)s%(device_id_str)s '
        '[%(name)s:%(lineno)d] %(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（按日期轮转）
    file_handler = logging.handlers.TimedRotatingFileHandler(
        os.path.join(log_dir, 'app.log'),
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 错误日志单独存储
    error_handler = logging.handlers.RotatingFileHandler(
        os.path.join(log_dir, 'error.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger

logger = setup_logger() 