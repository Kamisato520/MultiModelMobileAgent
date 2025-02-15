# backend/app/api/routes.py
from flask import Blueprint, request, jsonify, render_template
from app.services.automation_service import AutomationService
from app.services.llm_service import LLMService
from app.models.task import Task
from app import db
import asyncio

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
async def create_task():
    data = request.json
    device_id = data.get('device_id')
    input_type = data.get('input_type')  # 'text' or 'audio'
    input_content = data.get('input')

    if not device_id or not input_content:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # 根据输入类型选择不同的处理方法
        if input_type == 'text':
            execution_plan = await llm_service.analyze_text_input(input_content)
        elif input_type == 'audio':
            execution_plan = await llm_service.analyze_audio_input(input_content)
        else:
            return jsonify({'error': 'Invalid input type'}), 400

        # 创建并执行任务
        task = Task(device_id=device_id, user_input=input_content)
        task.execution_steps = execution_plan
        db.session.add(task)
        db.session.commit()

        # 连接设备
        device_connected = await automation_service.connect_device(device_id)
        if not device_connected:
            raise Exception("Failed to connect to device")

        # 开始执行任务
        asyncio.create_task(execute_task(task.id))

        return jsonify({
            'task_id': task.id,
            'status': 'pending'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

# 获取所有任务
@api.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

async def execute_task(task_id):
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

    except Exception as e:
        task.status = 'failed'
        task.result = {'error': str(e)}
        db.session.commit()

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
    try:
        data = request.json
        device_id = data.get('device_id')
        input_type = data.get('input_type', 'text')  # 默认为文本输入
        text_input = data.get('input')

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

        return jsonify({
            'status': 'success',
            'task_id': task_id,
            'result': task_result
        })

    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
