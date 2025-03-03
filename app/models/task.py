from enum import Enum
from datetime import datetime
from app import db
from typing import Dict, List, Optional
import json

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskResult(Enum):
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    INVALID_INSTRUCTION = "invalid_instruction"
    DEVICE_ERROR = "device_error"
    TIMEOUT = "timeout"

class Task(db.Model):
    """任务模型"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    device_id = db.Column(db.String(64), db.ForeignKey('device.device_id'))
    user_input = db.Column(db.Text)
    execution_steps = db.Column(db.JSON)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.PENDING)
    result = db.Column(db.Enum(TaskResult), nullable=True)
    error_message = db.Column(db.Text)
    
    # 执行反馈
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    execution_duration = db.Column(db.Float)  # 秒
    step_results = db.Column(db.JSON)  # 每个步骤的执行结果
    retry_count = db.Column(db.Integer, default=0)
    
    # 上下文信息
    context_id = db.Column(db.String(64))  # 多轮对话的上下文ID
    previous_task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    
    # LLM相关信息
    llm_response_time = db.Column(db.Float)  # LLM响应时间
    llm_token_count = db.Column(db.Integer)  # 使用的token数量
    prompt_template = db.Column(db.String(32))  # 使用的提示词模板

    def start_execution(self):
        """开始执行任务"""
        self.status = TaskStatus.RUNNING
        self.start_time = datetime.utcnow()
        db.session.commit()

    def complete_execution(self, result: TaskResult, error_message: str = None):
        """完成任务执行"""
        self.status = TaskStatus.COMPLETED if result == TaskResult.SUCCESS else TaskStatus.FAILED
        self.result = result
        self.error_message = error_message
        self.end_time = datetime.utcnow()
        self.execution_duration = (self.end_time - self.start_time).total_seconds()
        db.session.commit()

    def record_step_result(self, step_index: int, success: bool, error: str = None):
        """记录步骤执行结果"""
        if not self.step_results:
            self.step_results = []
            
        self.step_results.append({
            'step_index': step_index,
            'success': success,
            'error': error,
            'timestamp': datetime.utcnow().isoformat()
        })
        db.session.commit()

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'device_id': self.device_id,
            'user_input': self.user_input,
            'execution_steps': self.execution_steps,
            'status': self.status.value,
            'result': self.result.value if self.result else None,
            'error_message': self.error_message,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'execution_duration': self.execution_duration,
            'step_results': self.step_results,
            'retry_count': self.retry_count,
            'context_id': self.context_id,
            'previous_task_id': self.previous_task_id
        }

    @staticmethod
    def get_tasks_by_context(context_id: str) -> List['Task']:
        """获取同一上下文的所有任务"""
        return Task.query.filter_by(context_id=context_id).order_by(Task.start_time).all()
