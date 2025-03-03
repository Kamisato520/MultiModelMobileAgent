from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from app import db

def optimize_db_connection():
    """优化数据库连接池"""
    engine = create_engine(
        db.engine.url,
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800
    )
    
    db.session = scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    )
    
    return engine

def add_db_indexes():
    """添加数据库索引"""
    from app.models.task import Task
    from app.models.device import Device
    
    # 为常用查询添加索引
    db.Index('idx_task_status', Task.status)
    db.Index('idx_task_device_id', Task.device_id)
    db.Index('idx_device_status', Device.status)
    
    db.session.commit() 