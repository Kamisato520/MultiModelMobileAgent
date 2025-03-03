import pytest
from app.models.user import User
from app.models.device import Device
from app.models.task import Task

def test_user_password_hashing(test_user):
    """测试用户密码哈希功能"""
    assert test_user.check_password('password123')
    assert not test_user.check_password('wrongpassword')

def test_user_api_key_generation(db_session):
    """测试API密钥生成"""
    user = User(username='testuser2', email='test2@example.com')
    api_key = user.generate_api_key()
    assert api_key is not None
    assert len(api_key) == 64

def test_device_to_dict(test_device):
    """测试设备模型序列化"""
    device_dict = test_device.to_dict()
    assert device_dict['device_id'] == 'test_device_001'
    assert device_dict['name'] == 'Test Device'
    assert device_dict['platform'] == 'Android'

def test_task_to_dict(db_session, test_device):
    """测试任务模型序列化"""
    task = Task(
        device_id=test_device.device_id,
        user_input='test input',
        status='pending'
    )
    db_session.session.add(task)
    db_session.session.commit()
    
    task_dict = task.to_dict()
    assert task_dict['device_id'] == test_device.device_id
    assert task_dict['status'] == 'pending' 