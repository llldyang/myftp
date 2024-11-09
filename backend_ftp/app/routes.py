# routes.py
import json
from pipes import quote
from flask import Blueprint, redirect, url_for, jsonify, request, session, g, Response
from flask_socketio import emit, join_room, leave_room
from app.oauth import oauth  # 确保导入正确的 oauth 实例
import pyqrcode
from flask import send_file
from io import BytesIO
from app.auth import verify_totp, get_current_user
from app.models import db, User
from app.oauth import generate_totp_secret  # 假设这里有一个生成 TOTP 密钥的函数
import os
from werkzeug.utils import secure_filename, send_from_directory
from flask_cors import cross_origin
from app import socketio,limiter # 导入 socketio 实例
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import base64
import zipfile
import mimetypes
import hashlib
from flask_limiter import Limiter
from config import USER_BANDWIDTH_LIMITS
import time
import re
from pathlib import Path
from datetime import datetime  # 添加这行导入
from app.rate_limiter import create_rate_limiter

bp = Blueprint('auth', __name__)

# 初始化 MIME 类型
mimetypes.init()

def create_github_client(oauth):
    return oauth.register(
        name='github',
        client_id='Ov23liFT60ZSXOT6UfqI',
        client_secret='2edd5cb80dda5793699847ffb3c24272ddb33aaf',
        request_token_params={'scope': 'read:user'},
        access_token_url='https://github.com/login/oauth/access_token',
        access_token_params=None,
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )


# 使用全局 oauth 对象创建 GitHub 客户端
github = create_github_client(oauth)
print(f"GitHub Client: {github}")  # 打印 GitHub 客户端对象
print(f"Authorize URL: {github.authorize_url}")  # 检查 authorize_url


@bp.route('/login')
@limiter.limit("10 per second")  # 限制每个IP每秒最多10次请求
def login():
    redirect_uri = url_for('auth.authorized', _external=True)
    print(f"Redirect URI: {redirect_uri}")  # 添加调试语句
    print("login!!!!success!!!")
    return github.authorize_redirect(redirect_uri)  # 使用 authorize_redirect 方法进行重定向


@bp.route('/login/authorized')
@limiter.limit("10 per second")  # 限制每个IP每秒最多10次请求
def authorized():
    response = github.authorize_access_token()
    user_info = github.get('user').json()

    # 获取用户的主电子邮件地址
    email_info = github.get('user/emails').json()
    primary_email = next((email['email'] for email in email_info if email['primary']), None)
    print("primary_email")
    print(primary_email)
    # 查找或创建用户
    user = User.query.filter_by(username=user_info['login']).first()
    print(user)
    if not user:
        # 新建用户，生成 TOTP 密钥并创建二维码
        user = User(username=user_info['login'], email=primary_email)
        db.session.add(user)
        db.session.commit()

        # 生成 TOTP 密钥并保存到数据库
        totp_secret = generate_totp_secret()
        user.totp_secret = totp_secret
        db.session.commit()

        # 生成二维码
        otp_auth_url = f"otpauth://totp/MyApp:{user.username}?secret={totp_secret}&issuer=MyApp"
        qr_code = pyqrcode.create(otp_auth_url)
        buffer = BytesIO()
        qr_code.png(buffer, scale=5)
        buffer.seek(0)

        # 保存二维码和 TOTP 密钥到 session
        session['totp_qr_code'] = buffer.getvalue()
        session['totp_secret'] = totp_secret
        session['username'] = user.username
        # 将二维码图像编码为 Base64
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        # 创建 JWT Token
        access_token = create_access_token(identity=user.username)
        print("即将return")

        # 返回给前端，包含二维码和 token
        session['access_token'] = access_token
        session['qr_code_base64'] = qr_code_base64
        # return redirect(url_for('auth.show_qr_code'))  # 重定向到二维码页面
        # 显示二维码页面而非直接跳转至2FA
        print("显示二维码页面而非直接跳转至2FA")
        print(access_token)
        return redirect("https://localhost:8080/auth/qr-code")
    else:
        # 已有用户
        session['username'] = user.username
        session['totp_secret'] = user.totp_secret

        # 创建 JWT Token
        access_token = create_access_token(identity=user.username)
        session['access_token'] = access_token
        print(access_token)
        print("已存在用户")
        # 直接重定向到前端的 2FA 验证页面
        frontend_url = "https://localhost:8080/auth/2fa"
        return redirect(frontend_url)

# 新用户，生成二维码后跳转到验证页面前需要获取信息
@bp.route('/get_session_data', methods=['GET'])
@limiter.limit("10 per second")  # 限制每个IP每秒最多10次请求
def get_session_data():
    username = session.get('username')
    totp_secret = session.get('totp_secret')
    access_token = session.get('access_token')
    print(username,totp_secret)
    return jsonify({
        'username': username,
        'totp_secret': totp_secret,
        'access_token': access_token
    })

@bp.route('/2fa', methods=['GET'])
@limiter.limit("10 per second")  # 限制每个IP每秒最多10次请求
@jwt_required()  # 确保只有通过 JWT 鉴权的用户才能访问
def two_factor_auth():
    print("进入2fa")
    print(f"Session data: {session.items()}")  # 打印会话所有数据

    username = get_jwt_identity()
    print(f"Authenticated username in JWT: {username}")

    if not username:
        print("JWT token missing or invalid")
        return jsonify({'error': '未能找到有效的用户会话'}), 401

    return jsonify({
        'message': '进入2FA 验证页面',
        'username': username
    }), 200

@bp.route('/2fa/verify', methods=['POST'])
@limiter.limit("10 per second")  # 限制每个IP每秒最多10次请求
@jwt_required()
def two_factor_verify():
    print("进入2fa验证页面")
    # 从请求数据获取 TOTP 验证码
    totp_data = request.get_json()
    print(totp_data)
    totp = totp_data.get('totp')

    # 获取用户身份
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    g.user_type = user.user_type
    print(f"g.user_type: {g.user_type}")
    g.username = user.username

    print(f"TOTP received: {totp}, User found: {user}")
    # 检查 TOTP 验证
    if verify_totp(totp, user):
        return jsonify({'message': '验证成功'}), 200
    else:
        return jsonify({'error': '验证失败'}), 401

@bp.route('/show_qr_code')
@limiter.limit("10 per second")  # 限制每个IP每秒最多10次请求
def show_qr_code():
    qr_code_data = session.get('totp_qr_code')
    if not qr_code_data:
        return 'QR code not found', 404
    return send_file(BytesIO(qr_code_data), mimetype='image/png')


# Socket.IO 事件处理
@bp.route('/socket/test')
def socket_test():
    print("Socket.IO test route accessed.")
    return jsonify({"message": "Socket.IO test route"}), 200

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('response', {'message': 'You are connected!'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('join')
def on_join(data):
    username = data['username']
    join_room(username)
    print(f"{username} has joined the room.")

    emit('response', {'message': f'{username} has joined the room.'}, room=username)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    leave_room(username)
    print(f"{username} has left the room.")

    emit('response', {'message': f'{username} has left the room.'}, room=username)

# 文件上传和下载蓝图
upload_bp = Blueprint('upload', __name__)
# UPLOAD_FOLDER = 'static/uploads'
UPLOAD_ROOT = 'static/uploads'  # 基础文件夹
os.makedirs(UPLOAD_ROOT, exist_ok=True)  # 创建上传文件夹
os.chmod(UPLOAD_ROOT, 0o755)  # 设置适当的权限
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

# UPLOAD_FOLDER = 'static/uploads/str(get_user_upload_folder())'


# 全局变量用于存储上传进度
upload_progress = {}

def get_user_upload_folder(username):
    """根据用户名动态生成用户专属的文件夹路径"""
    user_folder = os.path.join(UPLOAD_ROOT, username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder, exist_ok=True)
        os.chmod(user_folder, 0o755)  # 设置适当的权限
    return user_folder
def update_upload_progress(filename, bytes_written, total_bytes, status):
    upload_progress[filename] = {
        'bytesWritten': bytes_written,
        'totalBytes': total_bytes,
        'status': status
    }


# 添加存储空间限制常量
STORAGE_LIMITS = {
    'regular': 10 * 1024 * 1024,  # 10MB
    'vip': 1024 * 1024 * 1024,    # 1GB
    'svip': 5 * 1024 * 1024 * 1024  # 5GB
}

def calculate_folder_size(folder_path):
    """计算文件夹的总大小"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

def get_storage_limit(user_type):
    """获取用户类型对应的存储空间限制"""
    return STORAGE_LIMITS.get(user_type, STORAGE_LIMITS['regular'])

def check_storage_space(user_type, file_size,username):
    """检查是否有足够的存储空间"""
    # 动态获取用户专属文件夹
    user_folder = get_user_upload_folder(username)  # 获取用户的根文件夹，文件名可以为空

    current_size = calculate_folder_size(user_folder)
    storage_limit = get_storage_limit(user_type)
    remaining_space = storage_limit - current_size
    return remaining_space >= file_size, remaining_space

def calculate_file_hash(file_path):
    """计算文件的SHA256哈希值"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# def get_bandwidth_limit(user_type):
#     """根据用户类型获取带宽限制"""
#     return USER_BANDWIDTH_LIMITS.get(user_type, USER_BANDWIDTH_LIMITS['regular'])

def get_bandwidth_limit(user_type):
    """根据用户类型返回带宽限制"""
    limits = {
        'regular': 0.05 * 1024 * 1024,  # 0.05 MB/s -> 524288 bytes/s
        'vip': 5 * 1024 * 1024,  # 5 MB/s -> 5242880 bytes/s
        'svip': 10 * 1024 * 1024  # 10 MB/s -> 10485760 bytes/s
    }
    return int(limits.get(user_type, 1 * 1024 * 1024))  # 默认1MB/s -> 1048576 bytes/s
def format_size(size):
    """将字节数转换为人类可读的格式"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def stream_file(file_path, bandwidth_limit):
    """流式传输文件，并应用带宽限制"""
    with open(file_path, 'rb') as f:
        while chunk := f.read(bandwidth_limit):
            yield chunk
            time.sleep(1)  # 每1秒发送带宽限制大小的字节数

def sanitize_filename(filename):
    """
    清理文件名但保留中文字符
    """
    # 移除危险字符但保留中文
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 确保文件名不以点或空格开始
    filename = filename.strip('. ')
    # 如果文件名为空，使用默认名称
    if not filename:
        filename = 'unnamed_file'
    return filename


import time


def write_with_bandwidth_limit(file, bandwidth_limit):
    """按照带宽限制将文件流写入目标文件"""
    start_time = time.time()  # 记录开始时间
    while True:
        # 读取带宽限制的字节数
        chunk = file.read(bandwidth_limit)
        if not chunk:
            break  # 如果文件已读完，退出循环

        # 写入文件
        file.write(chunk)

        # 计算花费时间
        elapsed_time = time.time() - start_time
        expected_time = len(chunk) / bandwidth_limit  # 根据带宽限制计算期望的时间
        sleep_time = expected_time - elapsed_time  # 如果传输太快，补偿时间
        if sleep_time > 0:
            time.sleep(sleep_time)
        start_time = time.time()  # 重置时间计时器


@upload_bp.route('/upload', methods=['POST', 'GET'])
@limiter.limit("10 per second")
def handle_upload():
    if request.method == 'GET':
        user = get_current_user()
        return jsonify({
            'progress': upload_progress
        })
    elif request.method == 'POST':
        return upload_files()
def update_upload_progress(filename, bytes_written, total_bytes, status):
    """更新上传进度信息"""
    upload_progress[filename] = {
        'bytesWritten': bytes_written,
        'totalBytes': total_bytes,
        'status': status,
        'percentage': (bytes_written / total_bytes * 100) if total_bytes > 0 else 0
    }
# def get_upload_progress():
#     user = get_current_user()
#     # 可以根据用户筛选进度信息
#     return jsonify({
#         'progress': upload_progress
#     })
# def upload_files():
#     user = get_current_user()
#     user_type = user['user_type']
#     print(f"/upload中user_type: {user_type}")
#     bandwidth_limit = get_bandwidth_limit(user_type)
#     uploaded_files = request.files.getlist('files')
#     file_hashes = {}
#
#     # 确保上传目录存在
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#
#     # 计算所有要上传文件的总大小
#     total_upload_size = 0
#     for file in uploaded_files:
#         if file.filename:
#             file.seek(0, os.SEEK_END)
#             total_upload_size += file.tell()
#             file.seek(0)
#
#     # 检查存储空间是否足够
#     has_space, remaining_space = check_storage_space(user_type, total_upload_size)
#     if not has_space:
#         storage_limit = get_storage_limit(user_type)
#         current_usage = calculate_folder_size(UPLOAD_FOLDER)
#         return jsonify({
#             'error': '存储空间不足',
#             'details': {
#                 'storage_limit': format_size(storage_limit),
#                 'current_usage': format_size(current_usage),
#                 'remaining_space': format_size(remaining_space),
#                 'required_space': format_size(total_upload_size)
#             }
#         }), 413  # 413 Payload Too Large
#
#
#     for file in uploaded_files:
#         if not file.filename:
#             continue
#         # 使用自定义的sanitize_filename函数处理文件名
#         original_filename = sanitize_filename(file.filename)
#
#         # 验证文件类型
#         if not allowed_file(original_filename):
#             return jsonify({
#                 'error': f'不支持的文件类型: {original_filename}',
#                 'allowed_types': list(ALLOWED_EXTENSIONS)
#             }), 400
#
#         # 处理文件名冲突
#         file_path = Path(UPLOAD_FOLDER) / original_filename
#         base_name = file_path.stem
#         suffix = file_path.suffix
#         counter = 1
#
#         while file_path.exists():
#             new_filename = f"{base_name}_{counter}{suffix}"
#             file_path = Path(UPLOAD_FOLDER) / new_filename
#             counter += 1
#
#         try:
#             # 分块写入文件并进行带宽限制
#             with open(file_path, 'wb') as f:
#                 while chunk := file.stream.read(bandwidth_limit):
#                     f.write(chunk)
#
#                     # time.sleep(1)  # 模拟带宽限制
#
#             # 计算和验证文件哈希
#             file_hash = calculate_file_hash(str(file_path))
#             client_hash = request.form.get(f'hash_{original_filename}')
#
#             if client_hash and client_hash != file_hash:
#                 os.remove(file_path)  # 删除可能被篡改的文件
#                 return jsonify({'error': f'文件 {original_filename} 被篡改'}), 400
#
#             file_hashes[original_filename] = {
#                 'hash': file_hash,
#                 'path': str(file_path.name),
#                 'size': file_path.stat().st_size,
#                 'upload_time': datetime.now().isoformat()
#             }
#
#         except Exception as e:
#             # 发生错误时清理
#             if file_path.exists():
#                 os.remove(file_path)
#             return jsonify({'error': f'上传文件 {original_filename} 时发生错误: {str(e)}'}), 500
#         # 添加存储使用情况到响应中
#         current_usage = calculate_folder_size(UPLOAD_FOLDER)
#         storage_limit = get_storage_limit(user_type)
#
#     return jsonify({
#         'status': 'success',
#         'message': f'成功上传 {len(file_hashes)} 个文件',
#         'uploaded_files': list(file_hashes.keys()),
#         'file_details': file_hashes,
#         'storage_info': {
#             'total_limit': format_size(storage_limit),
#             'current_usage': format_size(current_usage),
#             'remaining_space': format_size(storage_limit - current_usage),
#             'usage_percentage': round((current_usage / storage_limit) * 100, 2)
#         }
#     })
def upload_files():
    user = get_current_user()
    user_type = user['user_type']
    username = user['username']
    # 创建该用户的速率限制器
    rate_limiter = create_rate_limiter(user_type)

    uploaded_files = request.files.getlist('files')
    file_hashes = {}
    # 获取用户专属文件夹路径
    user_folder = get_user_upload_folder(username)
    # 确保上传目录存在
    os.makedirs(user_folder, exist_ok=True)

    # 计算总大小和验证存储空间
    total_upload_size = 0
    for file in uploaded_files:
        if file.filename:
            file.seek(0, os.SEEK_END)
            total_upload_size += file.tell()
            file.seek(0)

    # 检查存储空间
    has_space, remaining_space = check_storage_space(user_type, total_upload_size,username)
    if not has_space:
        return jsonify({
            'error': '存储空间不足',
            'details': {
                'storage_limit': format_size(get_storage_limit(user_type)),
                'current_usage': format_size(calculate_folder_size(user_folder)),
                'remaining_space': format_size(remaining_space),
                'required_space': format_size(total_upload_size)
            }
        }), 413

    try:
        for file in uploaded_files:
            if not file.filename:
                continue

            original_filename = sanitize_filename(file.filename)


            # 验证文件类型
            if not allowed_file(original_filename):
                return jsonify({
                    'error': f'不支持的文件类型: {original_filename}',
                    'allowed_types': list(ALLOWED_EXTENSIONS)
                }), 400

            # 处理文件名冲突
            file_path = Path(user_folder) / original_filename
            base_name = file_path.stem
            suffix = file_path.suffix
            counter = 1

            while file_path.exists():
                new_filename = f"{base_name}_{counter}{suffix}"
                file_path = Path(user_folder) / new_filename
                counter += 1



            bytes_written = 0
            file_size = file.content_length or 0

            update_upload_progress(original_filename, 0, file_size, 'uploading')

            # 分块写入文件并进行带宽限制
            CHUNK_SIZE = 810
            with open(file_path, 'wb') as f:

                while True:
                    chunk = file.stream.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    # 应用带宽限制
                    wait_time = rate_limiter.consume(len(chunk))
                    if wait_time > 0:
                        time.sleep(wait_time)

                    f.write(chunk)
                    bytes_written += len(chunk)

                    # 更新进度
                    update_upload_progress(original_filename, bytes_written, file_size, 'uploading')

            # 修改文件信息模拟上传过程中被修改/////////////////////////////////////////////////////////////////////////////
            with open(file_path, "a") as f:
                f.write("模拟篡改内容")

            # 计算和验证文件哈希
            file_hash = calculate_file_hash(str(file_path))
            client_hash = request.form.get(f'hash_{original_filename}')

            if client_hash and client_hash != file_hash:
                os.remove(file_path)
                return jsonify({'error': f'文件 {original_filename} 被篡改'}), 400

            file_hashes[original_filename] = {
                'hash': file_hash,
                'path': str(file_path.name),
                'size': file_path.stat().st_size,
                'upload_time': datetime.now().isoformat()
            }

    except Exception as e:
        # 发生错误时清理
        if 'file_path' in locals() and file_path.exists():
            os.remove(file_path)
        return jsonify({'error': f'上传文件时发生错误: {str(e)}'}), 500

    # 添加存储使用情况到响应中
    current_usage = calculate_folder_size(user_folder)
    storage_limit = get_storage_limit(user_type)

    return jsonify({
        'status': 'success',
        'message': f'成功上传 {len(file_hashes)} 个文件',
        'uploaded_files': list(file_hashes.keys()),
        'file_details': file_hashes,
        'storage_info': {
            'total_limit': format_size(storage_limit),
            'current_usage': format_size(current_usage),
            'remaining_space': format_size(storage_limit - current_usage),
            'usage_percentage': round((current_usage / storage_limit) * 100, 2)
        }
    })

# 列出文件夹中的文件
@upload_bp.route('/upload/download', methods=['GET'])
@limiter.limit("10 per second")  # 限制每个IP每秒最多10次请求
@cross_origin(supports_credentials=True)
# def download_all():
#     files = os.listdir(UPLOAD_FOLDER)
#     files_info = [{'name': file} for file in files]
#     return jsonify({'files': files_info}), 200
def get_available_files():
    user = get_current_user()
    # user_type = user['user_type']
    print(f"get_available_files中username: {user}")
    username = user['username']

    # 获取用户专属文件夹路径
    user_folder = get_user_upload_folder(username)
    try:
        files = []
        mime_type_mapping = {
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'application/msword',
            # 可添加更多映射
        }
        for filename in os.listdir(user_folder):
            file_path = os.path.join(user_folder, filename)
            if os.path.isfile(file_path):
                # 获取 MIME 类型
                file_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

                # 使用自定义映射字典
                file_type = mime_type_mapping.get(file_type, file_type)

                files.append({'name': filename, 'type': file_type})
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 单个文件下载
@upload_bp.route('/download/<filename>', methods=['GET'])
@limiter.limit("10 per second")  # 限制每个IP每秒最多10次请求
@cross_origin(supports_credentials=True)
def download_file(filename):
    user = get_current_user()
    user_type = user['user_type']
    username = user['username']

    # 获取用户专属文件夹路径
    user_folder = get_user_upload_folder(username)
    return send_from_directory(user_folder, filename, as_attachment=True)


@upload_bp.route('/upload/download/zip', methods=['POST'])
@limiter.limit("10 per second")
@cross_origin(supports_credentials=True)
def download_multiple_files():
    user = get_current_user()
    print(f"user:{user}")
    if user:
        username = user['username']
        user_type = user['user_type']
        print(f"下载zip时user_type", user_type)
        bandwidth_limit = get_bandwidth_limit(user_type)
        # user = get_current_user()
        # 获取用户专属文件夹路径
        user_folder = get_user_upload_folder(username)

        file_names = request.json.get('file_names')
        if not file_names:
            return jsonify({'error': '未选择文件'}), 400

        zip_buffer = BytesIO()
        file_hashes = {}

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename in file_names:
                # 直接使用原始文件名
                file_path = os.path.join(user_folder, filename)

                if not os.path.exists(file_path):
                    return jsonify({'error': f'文件 {filename} 不存在'}), 404

                try:
                    # 使用与上传时相同的哈希计算函数
                    file_hash = calculate_file_hash(file_path)
                    file_hashes[filename] = file_hash

                    # 将文件添加到ZIP中，使用原始文件名
                    zip_file.write(file_path, filename)

                except Exception as e:
                    return jsonify({'error': f'处理文件 {filename} 时发生错误: {str(e)}'}), 500

        # 重置缓冲区位置
        zip_buffer.seek(0)

        # 生成器函数，用于带宽限制
        def generate_zip_stream():
            while True:
                chunk = zip_buffer.read(bandwidth_limit)
                if not chunk:
                    break
                yield chunk
                time.sleep(1)

        response = Response(
            generate_zip_stream(),
            mimetype='application/zip',
        )

        # 设置下载文件名，支持中文
        filename = "selected_files.zip"
        response.headers['Content-Disposition'] = f"attachment; filename*=UTF-8''{quote(filename)}"

        # 添加文件哈希信息到响应头
        response.headers['X-File-Hashes'] = json.dumps(file_hashes)
        response.headers['Access-Control-Expose-Headers'] = 'X-File-Hashes, Content-Disposition'

        return response


@upload_bp.route('/upload/delete', methods=['POST'])
@limiter.limit("10 per second")
@cross_origin(supports_credentials=True)
def delete_files():
    user = get_current_user()
    user_type = user['user_type']
    username = user['username']

    # 获取用户专属文件夹路径
    user_folder = get_user_upload_folder(username)
    print("删除文件函数")
    user_type = g.get('user_type')
    print(user_type)
    filenames = request.get_json().get('filenames', [])
    if not filenames:
        return jsonify({'error': 'No files specified for deletion.'}), 400

    deleted_files = []
    for filename in filenames:
        file_path = os.path.join(user_folder, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_files.append(filename)
            except Exception as e:
                return jsonify({'error': f'Failed to delete file {filename}: {str(e)}'}), 500

    current_usage = calculate_folder_size(user_folder)
    storage_limit = get_storage_limit(user_type)
    return jsonify({
        'message': f'Deleted {len(deleted_files)} files successfully.',
        'deleted_files': deleted_files,
        'storage_info': {
            'total_limit': format_size(storage_limit),
            'current_usage': format_size(current_usage),
            'remaining_space': format_size(storage_limit - current_usage),
            'usage_percentage': round((current_usage / storage_limit) * 100, 2)
        }
    })



@upload_bp.route('/upload/usage', methods=['GET'])
@limiter.limit("10 per second")
@cross_origin(supports_credentials=True)
def get_storage_usage():
    try:
        print("usage请求获取用户")
        user = get_current_user()
        if user:
            username = user['username']
            user_type = user['user_type']
            # 获取用户专属文件夹路径
            user_folder = get_user_upload_folder(username)
            current_size = calculate_folder_size(user_folder)
            storage_limit = get_storage_limit(user_type)
            remaining_space = storage_limit - current_size
            print(username, user_type, current_size, remaining_space)
            return jsonify({
                'username': username,
                'user_type': user_type,
                'used_space': format_size(current_size),
                'total_space': format_size(storage_limit),
                'remaining_space': format_size(remaining_space)
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500