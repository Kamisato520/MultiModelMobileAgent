import pytest
import json
from app.models.task import Task

def test_create_task(client, auth_headers, test_device):
    """测试任务创建API"""
    response = client.post('/api/tasks', 
        headers=auth_headers,
        json={
            'device_id': test_device.device_id,
            'input_type': 'text',
            'input': 'test input'
        }
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'task_id' in data
    assert data['status'] == 'pending'

def test_get_devices(client, auth_headers, test_device):
    """测试获取设备列表API"""
    response = client.get('/api/devices', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
    assert data[0]['device_id'] == test_device.device_id

def test_unauthorized_access(client):
    """测试未授权访问"""
    response = client.get('/api/devices')
    assert response.status_code == 401

def test_admin_access(client, test_admin):
    """测试管理员访问权限"""
    headers = {
        'X-API-Key': test_admin.api_key,
        'Content-Type': 'application/json'
    }
    response = client.get('/api/admin/users', headers=headers)
    assert response.status_code == 200 