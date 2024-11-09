import os

class Config:
    SECRET_KEY = 'random_secret_key'  # 在生产环境中请使用安全的随机密钥
    DEBUG = True  # 开发环境中设置为 True，生产环境中应设置为 False
    # 数据库配置

    # HTTPS 配置
    SSL_CERT_FILE = os.path.join(os.path.dirname(__file__), './certs/localhost.crt')  # 指向证书文件
    SSL_KEY_FILE = os.path.join(os.path.dirname(__file__), './certs/Server_key.key')  # 指向私钥文件
    CA_CERT_FILE = os.path.join(os.path.dirname(__file__), './certs/my_CA.crt')  # 指向 CA 证书文件


# 每个用户类型的带宽限制 (bytes per second)
USER_BANDWIDTH_LIMITS = {
    'regular': 0.05 * 1024 * 1024,  # 1 MB/s
    'vip': 5 * 1024 * 1024       # 5 MB/s
}