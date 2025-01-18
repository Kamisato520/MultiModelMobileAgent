from datetime import datetime
from app import db

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), nullable=False)
    user_input = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    execution_steps = db.Column(db.JSON)
    result = db.Column(db.JSON)

    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'execution_steps': self.execution_steps,
            'result': self.result
        }
