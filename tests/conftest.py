import pytest
from app import create_app, db
from app.models.user import User
from app.models.device import Device
from app.models.task import Task

@pytest.fixture
def app():
    """创建测试应用实例"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })
    return app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """创建CLI测试运行器"""
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    """设置数据库会话"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = User(
        username='testuser',
        email='test@example.com',
        role='user'
    )
    user.set_password('password123')
    user.generate_api_key()
    db_session.session.add(user)
    db_session.session.commit()
    return user

@pytest.fixture
def test_admin(db_session):
    """创建测试管理员"""
    admin = User(
        username='admin',
        email='admin@example.com',
        role='admin'
    )
    admin.set_password('admin123')
    admin.generate_api_key()
    db_session.session.add(admin)
    db_session.session.commit()
    return admin

@pytest.fixture
def test_device(db_session):
    """创建测试设备"""
    device = Device(
        device_id='test_device_001',
        name='Test Device',
        platform='Android'
    )
    db_session.session.add(device)
    db_session.session.commit()
    return device

@pytest.fixture
def auth_headers(test_user):
    """生成认证头"""
    return {
        'X-API-Key': test_user.api_key,
        'Content-Type': 'application/json'
    } 