# 使用官方Python镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . /app

# 设置多个pip源为国内镜像，提高下载速度和成功率
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config set global.extra-index-url \
    https://mirrors.aliyun.com/pypi/simple/ \
    https://pypi.doubanio.com/simple/ \
    https://pypi.mirrors.ustc.edu.cn/simple/

# 更新apt源为中国镜像
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list

# 安装系统依赖和Python依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        fonts-wqy-microhei \
        build-essential \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt \
    || pip install --no-cache-dir -r requirements.txt \
    || pip install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# 暴露端口5000供外部访问
EXPOSE 5000

# 运行应用
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
