# backend/app/api/routes.py
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.services.automation_service import AutomationService
from app.services.llm_service import LLMService
from app.models.task import Task
from app.models.device import Device
from app.models.user import User  # 添加User模型导入
from app import db
import asyncio
from app.utils.logger import logger
from app.utils.exceptions import TaskError, format_error_response
from app.utils.auth import require_api_key, require_admin

api = Blueprint('api', __name__)
automation_service = AutomationService()
llm_service = LLMService()

# 添加根路由
@api.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'message': 'API server is running'
    })

# 添加健康检查路由
@api.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'services': {
            'database': 'connected',
            'websocket': 'running'
        }
    })

@api.route('/tasks', methods=['POST'])
@require_api_key
async def create_task():
    try:
        data = request.json
        device_id = data.get('device_id')
        input_type = data.get('input_type')
        input_content = data.get('input')

        logger.info(f"Creating new task for device {device_id}",
                   extra={'device_id': device_id})

        if not device_id or not input_content:
            raise TaskError("Missing required fields")

        # 根据输入类型选择不同的处理方法
        if input_type == 'text':
            execution_plan = await llm_service.analyze_text_input(input_content)
        elif input_type == 'audio':
            execution_plan = await llm_service.analyze_audio_input(input_content)
        else:
            raise TaskError("Invalid input type")

        # 创建任务
        task = Task(
            device_id=device_id,
            user_input=input_content,
            user_id=current_user.id  # 添加用户ID关联
        )
        task.execution_steps = execution_plan
        db.session.add(task)
        db.session.commit()

        # 连接设备
        device_connected = await automation_service.connect_device(device_id)
        if not device_connected:
            raise TaskError("Failed to connect to device")

        # 开始执行任务
        asyncio.create_task(execute_task(task.id))

        logger.info(f"Task {task.id} created successfully",
                   extra={'task_id': task.id, 'device_id': device_id})

        return jsonify({
            'task_id': task.id,
            'status': 'pending'
        })

    except Exception as e:
        logger.error("Failed to create task", exc_info=True,
                    extra={'device_id': device_id if device_id else None})
        return jsonify(format_error_response(e)), 500

@api.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    # 检查任务是否属于当前用户或用户是否为管理员
    if task.user_id != current_user.id and current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(task.to_dict())

@api.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    # 普通用户只能看到自己的任务，管理员可以看到所有任务
    if current_user.role == 'admin':
        tasks = Task.query.all()
    else:
        tasks = Task.query.filter_by(user_id=current_user.id).all()
    return jsonify([task.to_dict() for task in tasks])

@api.route('/devices', methods=['GET'])
@login_required
def get_devices():
    try:
        # 获取所有设备
        devices = Device.query.all()
        
        # 获取设备的实时状态
        device_list = []
        for device in devices:
            device_info = device.to_dict()
            # 添加实时连接状态
            device_info['connected'] = automation_service.is_device_connected(device.device_id)
            device_list.append(device_info)
            
        return jsonify(device_list)
    except Exception as e:
        logger.error("Failed to get devices", exc_info=True)
        return jsonify(format_error_response(e)), 500

@api.route('/devices/<string:device_id>', methods=['GET'])
@login_required
def get_device(device_id):
    try:
        device = Device.query.filter_by(device_id=device_id).first_or_404()
        device_info = device.to_dict()
        # 添加实时状态信息
        device_info.update(automation_service.get_device_info(device_id))
        return jsonify(device_info)
    except Exception as e:
        logger.error(f"Failed to get device info: {device_id}", exc_info=True)
        return jsonify(format_error_response(e)), 500

@api.route('/devices/<string:device_id>/disconnect', methods=['POST'])
@login_required
async def disconnect_device(device_id):
    try:
        success = await automation_service.disconnect_device(device_id)
        if success:
            return jsonify({'message': 'Device disconnected successfully'})
        return jsonify({'error': 'Failed to disconnect device'}), 400
    except Exception as e:
        logger.error(f"Failed to disconnect device: {device_id}", exc_info=True)
        return jsonify(format_error_response(e)), 500

@api.route('/admin/users', methods=['GET'])
@require_admin
def get_users():
    try:
        users = User.query.all()
        return jsonify([{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active
        } for user in users])
    except Exception as e:
        logger.error("Failed to get users", exc_info=True)
        return jsonify(format_error_response(e)), 500

@api.route('/admin/users/<int:user_id>', methods=['PUT'])
@require_admin
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
            
        db.session.commit()
        logger.info(f"User {user_id} updated by admin {current_user.username}")
        
        return jsonify({
            'message': 'User updated successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'role': user.role,
                'is_active': user.is_active
            }
        })
    except Exception as e:
        logger.error(f"Failed to update user: {user_id}", exc_info=True)
        return jsonify(format_error_response(e)), 500

async def execute_task(task_id):
    """异步执行任务"""
    task = Task.query.get(task_id)
    if not task:
        return

    try:
        task.status = 'running'
        db.session.commit()

        for step in task.execution_steps:
            success = await automation_service.execute_action(
                task.device_id, 
                step
            )
            if not success:
                raise Exception(f"Failed to execute step: {step}")

        task.status = 'completed'
        task.result = {'success': True}
        db.session.commit()
        
        logger.info(f"Task {task_id} completed successfully",
                   extra={'task_id': task_id})

    except Exception as e:
        task.status = 'failed'
        task.result = {'error': str(e)}
        db.session.commit()
        
        logger.error(f"Task {task_id} failed: {str(e)}",
                    exc_info=True, extra={'task_id': task_id})

<<<<<<< HEAD
@api.route('/test')
def test_page():
    return render_template('test.html')

@api.route('/test/llm', methods=['POST'])
@login_required
async def test_llm():
=======
# 自动化测试
@api.route('/test/auto', methods=['POST'])
async def create_task_test(task_data):
    # 模拟调用 create_task 接口
    from flask import Flask, request
    app = Flask(__name__)
    with app.test_request_context('/tasks', method='POST', json=task_data):
        response = await create_task()
        return response.get_json()
    
def get_task_test(task_id):
    # 模拟调用 get_task 接口
    from flask import Flask, request
    app = Flask(__name__)
    with app.test_request_context(f'/tasks/{task_id}', method='GET'):
        response = get_task(task_id)
        return response.get_json()

async def wait_for_task_completion(task_id, timeout=30):
    import time
    start_time = time.time()
    while time.time() - start_time < timeout:
        task = Task.query.get(task_id)
        if task.status in ['completed', 'failed']:
            break
        await asyncio.sleep(1)
    else:
        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")
async def test_auto():
>>>>>>> 6c147b24167bdfa1032c9398fdff06cd64a5fc9d
    try:
        data = request.json
        device_id = data.get('device_id')
        input_type = data.get('input_type', 'text')  # 默认为文本输入
        text_input = data.get('input')
<<<<<<< HEAD
        
        if not text_input:
            return jsonify({'error': 'No input provided'}), 400
            
        # 调用LLM服务
        execution_steps = await llm_service.analyze_text_input(text_input)
        
=======

        # 检查必要参数
        if not device_id or not text_input:
            return jsonify({'error': 'Missing required fields'}), 400

        # 创建任务
        task_data = {
            'device_id': device_id,
            'input_type': input_type,
            'input': text_input
        }
        create_response = await create_task_test(task_data)

        # 检查任务是否创建成功
        if create_response.get('status') != 'pending':
            return jsonify({
                'error': 'Failed to create task',
                'response': create_response
            }), 500

        task_id = create_response.get('task_id')

        # 等待任务执行完成
        await wait_for_task_completion(task_id)

        # 获取任务结果
        task_result = get_task_test(task_id)

>>>>>>> 6c147b24167bdfa1032c9398fdff06cd64a5fc9d
        return jsonify({
            'status': 'success',
            'task_id': task_id,
            'result': task_result
        })

    except Exception as e:
<<<<<<< HEAD
        logger.error("LLM test failed", exc_info=True)
        return jsonify(format_error_response(e)), 500
=======
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
>>>>>>> 6c147b24167bdfa1032c9398fdff06cd64a5fc9d
