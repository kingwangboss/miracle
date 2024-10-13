# 使用官方Ubuntu镜像作为基础镜像
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
    git \
    fonts-wqy-microhei \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 克隆项目代码（带重试机制）
RUN for i in {1..5}; do \
        git clone https://github.com/kingwangboss/miracle.git . && break || sleep 15; \
    done

# 如果克隆失败，则从本地复制代码
COPY . /app

# 安装项目依赖
RUN pip3 install --no-cache-dir -r requirements.txt

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=production

# 暴露端口5000供外部访问
EXPOSE 5000

# 使用gunicorn作为生产环境的WSGI服务器
RUN pip3 install gunicorn

# 设置启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
