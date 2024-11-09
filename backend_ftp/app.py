# app.py
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from flask import Flask, g
from app import create_app, socketio, db  # 导入 create_app 和 socketio
from app.auth import get_current_user  # 导入 get_current_user

app = create_app()  # 使用 create_app 函数创建应用实例
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "https://localhost:8080"}})

migrate = Migrate(app, db)

# @app.before_request
# def load_user():
#     # 每次请求之前加载token 用户信息
#     print("开始请求g.user = get_current_user()")
#     g.user = get_current_user()


@app.route('/file-manager')
def file_manager():
    return '文件管理页面'

if __name__ == '__main__':
    socketio.run(app, ssl_context=(Config.SSL_CERT_FILE, Config.SSL_KEY_FILE), host='localhost', port=5000, debug=True)
