# 使用官方Python运行时作为父镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装中文字体
RUN apt-get update && apt-get install -y fonts-wqy-microhei && apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# 暴露端口5000供外部访问
EXPOSE 5000

# 使用gunicorn作为生产环境的WSGI服务器
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
