from . import db  # 从当前包导入 db 实例

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    totp_secret = db.Column(db.String(36), nullable=True)  # 用于存储 TOTP 密钥
    user_type = db.Column(db.String(20), default="regular")  # 新增字段，用户类型

    def __repr__(self):
        return f'<User {self.username}>'

