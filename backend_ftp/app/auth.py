import pyotp
from app.models import User
from flask import request, jsonify, current_app, g
import jwt
def verify_totp(totp, user):

    if user and user.totp_secret:
        totp_verifier = pyotp.TOTP(user.totp_secret)
        return totp_verifier.verify(totp)
    return False


def get_current_user():
    # 获取授权头的 JWT token
    token = request.headers.get('Authorization')
    print(f"auth中token: {token}")
    if token is None:
        return None

    try:
        # 获取 JWT 密钥
        secret_key = current_app.config['JWT_SECRET_KEY']
        token = token.split(" ")[1]  # 提取 JWT token (格式为 'Bearer <token>')

        # 解码 JWT token 获取用户 ID
        data = jwt.decode(token, secret_key, algorithms=["HS256"])
        username = data.get("sub")
        print(f"username: {username}")
        # 根据用户名查询用户
        if username:
            user = User.query.filter_by(username=username).first()  # 获取单个用户对象
            if user:
                # 返回用户的完整信息
                return {
                    'username': user.username,
                    'user_type': user.user_type,
                    'email': user.email,  # 根据需要添加更多字段
                    'id': user.id,
                    # 添加其他需要的字段
                }
            else:
                return None
        else:
            return None
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
        # 记录错误并返回 None
        current_app.logger.error(f"JWT 解码失败: {e}")
        return None