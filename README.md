# MultiModelMobileAgent
developing
backend/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py
│   │   └── device.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── automation_service.py
│   │   ├── llm_service.py
│   │   └── websocket_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── websocket.py
│   └── utils/
│       ├── __init__.py
│       └── response.py
└── run.py
## 下面是test的地址
ttp://127.0.0.1:5000/ - 显示服务器状态
http://127.0.0.1:5000/api/ - 显示 API 状态
http://127.0.0.1:5000/api/health - 显示健康检查状态
http://127.0.0.1:5000/api/tasks - 获取所有任务（GET）或创建新任务（POST）
http://127.0.0.1:5000/api/tasks/<task_id> - 获取特定任务的详情
