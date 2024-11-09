# # 文件上传和下载蓝图
# upload_bp = Blueprint('upload', __name__)
# UPLOAD_FOLDER = 'static/uploads'
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 创建上传文件夹
# os.chmod(UPLOAD_FOLDER, 0o755)  # 设置适当的权限
# ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
#
# # 添加存储空间限制常量
# STORAGE_LIMITS = {
#     'regular': 10 * 1024 * 1024,  # 10MB
#     'vip': 1024 * 1024 * 1024,    # 1GB
#     'svip': 5 * 1024 * 1024 * 1024  # 5GB
# }
#
# def calculate_folder_size(folder_path):
#     """计算文件夹的总大小"""
#     total_size = 0
#     for dirpath, dirnames, filenames in os.walk(folder_path):
#         for filename in filenames:
#             file_path = os.path.join(dirpath, filename)
#             total_size += os.path.getsize(file_path)
#     return total_size
#
# def get_storage_limit(user_type):
#     """获取用户类型对应的存储空间限制"""
#     return STORAGE_LIMITS.get(user_type, STORAGE_LIMITS['regular'])
#
# def check_storage_space(user_type, file_size):
#     """检查是否有足够的存储空间"""
#     current_size = calculate_folder_size(UPLOAD_FOLDER)
#     storage_limit = get_storage_limit(user_type)
#     remaining_space = storage_limit - current_size
#     return remaining_space >= file_size, remaining_space
#
# def calculate_file_hash(file_path):
#     """计算文件的SHA256哈希值"""
#     hash_sha256 = hashlib.sha256()
#     with open(file_path, 'rb') as f:
#         for chunk in iter(lambda: f.read(4096), b""):
#             hash_sha256.update(chunk)
#     return hash_sha256.hexdigest()
#
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#
#
# # def get_bandwidth_limit(user_type):
# #     """根据用户类型获取带宽限制"""
# #     return USER_BANDWIDTH_LIMITS.get(user_type, USER_BANDWIDTH_LIMITS['regular'])
#
# def get_bandwidth_limit(user_type):
#     """根据用户类型返回带宽限制"""
#     limits = {
#         'regular': 1024 * 1024,  # 1MB/s
#         'vip': 5 * 1024 * 1024,  # 5MB/s
#         'svip': 10 * 1024 * 1024  # 10MB/s
#     }
#     return limits.get(user_type, 1024 * 1024)  # 默认1MB/s
#
# def format_size(size):
#     """将字节数转换为人类可读的格式"""
#     for unit in ['B', 'KB', 'MB', 'GB']:
#         if size < 1024:
#             return f"{size:.2f} {unit}"
#         size /= 1024
#     return f"{size:.2f} TB"
#
#
# def stream_file(file_path, bandwidth_limit):
#     """流式传输文件，并应用带宽限制"""
#     with open(file_path, 'rb') as f:
#         while chunk := f.read(bandwidth_limit):
#             yield chunk
#             time.sleep(1)  # 每1秒发送带宽限制大小的字节数
#
# def sanitize_filename(filename):
#     """
#     清理文件名但保留中文字符
#     """
#     # 移除危险字符但保留中文
#     filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
#     # 确保文件名不以点或空格开始
#     filename = filename.strip('. ')
#     # 如果文件名为空，使用默认名称
#     if not filename:
#         filename = 'unnamed_file'
#     return filename
#
# # 列出文件夹中的文件
# @upload_bp.route('/upload/download', methods=['GET'])
# @limiter.limit("10 per second")  # 限制每个IP每秒最多10次请求
# @cross_origin(supports_credentials=True)
# # def download_all():
# #     files = os.listdir(UPLOAD_FOLDER)
# #     files_info = [{'name': file} for file in files]
# #     return jsonify({'files': files_info}), 200
# def get_available_files():
#     try:
#         files = []
#         mime_type_mapping = {
#             'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'application/msword',
#             # 可添加更多映射
#         }
#         for filename in os.listdir(UPLOAD_FOLDER):
#             file_path = os.path.join(UPLOAD_FOLDER, filename)
#             if os.path.isfile(file_path):
#                 # 获取 MIME 类型
#                 file_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
#
#                 # 使用自定义映射字典
#                 file_type = mime_type_mapping.get(file_type, file_type)
#
#                 files.append({'name': filename, 'type': file_type})
#         return jsonify({'files': files}), 200
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500




# @upload_bp.route('/upload', methods=['POST', 'GET'])
# @limiter.limit("10 per second")
# def handle_upload():
#     if request.method == 'GET':
#         user = get_current_user()
#         return jsonify({
#             'progress': upload_progress
#         })
#     elif request.method == 'POST':
#         return upload_files()
# def update_upload_progress(filename, bytes_written, total_bytes, status):
#     """更新上传进度信息"""
#     upload_progress[filename] = {
#         'bytesWritten': bytes_written,
#         'totalBytes': total_bytes,
#         'status': status,
#         'percentage': (bytes_written / total_bytes * 100) if total_bytes > 0 else 0
#     }
# def upload_files():
#     user = get_current_user()
#     user_type = user['user_type']
#
#     # 创建该用户的速率限制器
#     rate_limiter = create_rate_limiter(user_type)
#
#     uploaded_files = request.files.getlist('files')
#     file_hashes = {}
#
#     # 确保上传目录存在
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#
#     # 计算总大小和验证存储空间
#     total_upload_size = 0
#     for file in uploaded_files:
#         if file.filename:
#             file.seek(0, os.SEEK_END)
#             total_upload_size += file.tell()
#             file.seek(0)
#
#     # 检查存储空间
#     has_space, remaining_space = check_storage_space(user_type, total_upload_size)
#     if not has_space:
#         return jsonify({
#             'error': '存储空间不足',
#             'details': {
#                 'storage_limit': format_size(get_storage_limit(user_type)),
#                 'current_usage': format_size(calculate_folder_size(UPLOAD_FOLDER)),
#                 'remaining_space': format_size(remaining_space),
#                 'required_space': format_size(total_upload_size)
#             }
#         }), 413
#
#     try:
#         for file in uploaded_files:
#             if not file.filename:
#                 continue
#
#             original_filename = sanitize_filename(file.filename)
#
#
#             # 验证文件类型
#             if not allowed_file(original_filename):
#                 return jsonify({
#                     'error': f'不支持的文件类型: {original_filename}',
#                     'allowed_types': list(ALLOWED_EXTENSIONS)
#                 }), 400
#
#             # 处理文件名冲突
#             file_path = Path(UPLOAD_FOLDER) / original_filename
#             base_name = file_path.stem
#             suffix = file_path.suffix
#             counter = 1
#
#             while file_path.exists():
#                 new_filename = f"{base_name}_{counter}{suffix}"
#                 file_path = Path(UPLOAD_FOLDER) / new_filename
#                 counter += 1
#
#             bytes_written = 0
#             file_size = file.content_length or 0
#
#             update_upload_progress(original_filename, 0, file_size, 'uploading')
#
#             # 分块写入文件并进行带宽限制
#             CHUNK_SIZE = 810
#             with open(file_path, 'wb') as f:
#                 while True:
#                     chunk = file.stream.read(CHUNK_SIZE)
#                     if not chunk:
#                         break
#
#                     # 应用带宽限制
#                     wait_time = rate_limiter.consume(len(chunk))
#                     if wait_time > 0:
#                         time.sleep(wait_time)
#
#                     f.write(chunk)
#                     bytes_written += len(chunk)
#
#                     # 更新进度
#                     update_upload_progress(original_filename, bytes_written, file_size, 'uploading')
#
#             # 计算和验证文件哈希
#             file_hash = calculate_file_hash(str(file_path))
#             client_hash = request.form.get(f'hash_{original_filename}')
#
#             if client_hash and client_hash != file_hash:
#                 os.remove(file_path)
#                 return jsonify({'error': f'文件 {original_filename} 被篡改'}), 400
#
#             file_hashes[original_filename] = {
#                 'hash': file_hash,
#                 'path': str(file_path.name),
#                 'size': file_path.stat().st_size,
#                 'upload_time': datetime.now().isoformat()
#             }
#
#     except Exception as e:
#         # 发生错误时清理
#         if 'file_path' in locals() and file_path.exists():
#             os.remove(file_path)
#         return jsonify({'error': f'上传文件时发生错误: {str(e)}'}), 500
#
#     # 添加存储使用情况到响应中
#     current_usage = calculate_folder_size(UPLOAD_FOLDER)
#     storage_limit = get_storage_limit(user_type)
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
#
