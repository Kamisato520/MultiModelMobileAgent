from datetime import datetime
from app import db

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100))
    platform = db.Column(db.String(20), nullable=False)  # Android/iOS
    status = db.Column(db.String(20), default='offline')  # online/offline/busy
    last_connected = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'device_id': self.device_id,
            'name': self.name,
            'platform': self.platform,
            'status': self.status,
            'last_connected': self.last_connected.isoformat() if self.last_connected else None,
            'created_at': self.created_at.isoformat()
        }
