# app/oauth.py
import pyotp
from authlib.integrations.flask_client import OAuth

oauth = OAuth()  # 创建一个 OAuth 实例

def init_app(app):
    oauth.init_app(app)  # 将 Flask 应用传递给 OAuth 实例


def get_user():
    pass


def verify_totp(totp):
    user = get_user()  # 获取用户数据的函数
    if user is None:
        raise Exception("User not found")  # 确保 user 不为 None
    totp_obj = pyotp.TOTP(user['totp_secret'])  # 确保 totp_secret 有效
    return totp_obj.verify(totp)

def generate_totp_secret():
    return pyotp.random_base32()  # 生成 TOTP 秘钥