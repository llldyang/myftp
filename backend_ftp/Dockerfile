 # 使用官方 Python 镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录的内容到容器中的 /app 目录
COPY . /app

# 安装 Flask 项目所需的依赖
RUN pip install --no-cache-dir -r requirements.txt

# 开放容器的 5000 端口
EXPOSE 5000

# 设置容器启动时运行的命令
CMD ["python", "app.py"]

