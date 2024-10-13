# 使用Ubuntu作为基础镜像，这确保了Linux环境
FROM ubuntu:20.04

# 避免交互式前端
ENV DEBIAN_FRONTEND=noninteractive

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 更新apt源并安装必要的软件
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    fonts-wqy-microhei \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件到容器中
COPY . /app

# 使用国内PyPI镜像源，增加重试次数和超时时间
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 分步安装依赖
RUN pip3 install --no-cache-dir -r requirements.txt --retries 10 --timeout 600 || \
    (pip3 install --no-cache-dir -r requirements.txt --retries 10 --timeout 600 && \
     pip3 install --no-cache-dir -r requirements.txt --retries 10 --timeout 600)

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# 暴露端口5000供外部访问
EXPOSE 5000

# 使用gunicorn作为生产环境的WSGI服务器
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
