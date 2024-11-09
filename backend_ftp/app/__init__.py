import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from config import Config  # 导入 Config 类
from flask_jwt_extended import JWTManager  # 新增导入 JWTManager
from flask_limiter import Limiter  # 导入 Flask-Limiter
from flask_limiter.util import get_remote_address  # 导入获取用户IP的工具
# 创建 SocketIO 和 SQLAlchemy 实例
socketio = SocketIO(cors_allowed_origins='*')  # 允许所有源进行连接
db = SQLAlchemy()
jwt = JWTManager()  # 新增 JWT 实例
limiter = Limiter(key_func=get_remote_address)  # 初始化 Limiter

def create_app():
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(Config)  # 加载 Config 配置
    app.config["JWT_SECRET_KEY"] = "your_jwt_secret_key"  # 配置 JWT 密钥
    # 配置数据库信息
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/filetrans'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 例如限制为16MB
    # 初始化 SocketIO 和 SQLAlchemy
    socketio.init_app(app)  # 这里初始化 SocketIO
    db.init_app(app)
    jwt.init_app(app)  # 初始化 JWT
    limiter.init_app(app)  # 初始化请求限制器

    # 在应用上下文中导入模型并创建表
    with app.app_context():
        from .models import User  # 确保在应用上下文中导入模型
        print("User model imported successfully.")

        # 创建所有数据库表
        print("Creating all tables...")
        db.create_all()

    # 导入 OAuth 的初始化方法并初始化
    from .oauth import init_app as init_oauth
    init_oauth(app)  # 初始化 OAuth 实例

    # 注册蓝图
    from .routes import upload_bp, bp as auth_bp  # 在函数内部导入蓝图
    app.register_blueprint(upload_bp)  # 注册文件上传蓝图
    app.register_blueprint(auth_bp, url_prefix='/auth')  # 注册认证蓝图

    return app
