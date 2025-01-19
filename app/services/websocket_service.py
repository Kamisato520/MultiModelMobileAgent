# backend/app/services/websocket_service.py
import asyncio
import websockets
import json
from app.models.task import Task
from app.models.device import Device
from datetime import datetime
from app import db

class WebSocketService:
    def __init__(self):
        self.connections = {}  # 存储设备连接
        self.device_status = {}  # 存储设备状态

    async def register(self, device_id: str, websocket):
        """注册新的设备连接"""
        self.connections[device_id] = websocket
        
        # 更新设备状态
        device = Device.query.filter_by(device_id=device_id).first()
        if device:
            device.status = 'online'
            device.last_connected = datetime.utcnow()
            db.session.commit()
        
        self.device_status[device_id] = 'online'

    async def unregister(self, device_id: str):
        """注销设备连接"""
        if device_id in self.connections:
            del self.connections[device_id]
            
            # 更新设备状态
            device = Device.query.filter_by(device_id=device_id).first()
            if device:
                device.status = 'offline'
                db.session.commit()
            
            self.device_status[device_id] = 'offline'

    async def send_update(self, device_id: str, data: dict):
        """向指定设备发送更新"""
        if device_id in self.connections:
            try:
                await self.connections[device_id].send(json.dumps(data))
                return True
            except Exception as e:
                await self.unregister(device_id)
                return False
        return False

    async def handle_connection(self, websocket, path):
        """处理WebSocket连接"""
        device_id = None
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data['type'] == 'register':
                        device_id = data['device_id']
                        await self.register(device_id, websocket)
                        await websocket.send(json.dumps({
                            'type': 'registered',
                            'device_id': device_id,
                            'status': 'success'
                        }))
                    elif data['type'] == 'status_update':
                        if device_id:
                            self.device_status[device_id] = data.get('status', 'online')
                    elif data['type'] == 'task_update':
                        # 处理任务更新
                        task_id = data.get('task_id')
                        status = data.get('status')
                        if task_id and status:
                            task = Task.query.get(task_id)
                            if task:
                                task.status = status
                                if 'result' in data:
                                    task.result = data['result']
                                db.session.commit()
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    }))
                except Exception as e:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': str(e)
                    }))
        finally:
            if device_id:
                await self.unregister(device_id)

    def get_device_status(self, device_id: str) -> str:
        """获取设备状态"""
        return self.device_status.get(device_id, 'offline')

    def is_device_connected(self, device_id: str) -> bool:
        """检查设备是否连接"""
        return device_id in self.connections