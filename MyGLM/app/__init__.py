from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

# 初始化数据库
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)

    # 注册蓝图
    from app.api.routes import api
    app.register_blueprint(api, url_prefix='/api')

    # 添加根路由
    @app.route('/')
    def index():
        return jsonify({
            'status': 'ok',
            'message': 'Server is running',
            'api_docs': '/api'
        })

    # 创建数据库表
    with app.app_context():
        db.create_all()

    return app
