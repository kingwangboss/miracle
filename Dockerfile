# 使用官方Python运行时作为父镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装git（用于克隆代码）
RUN apt-get update && apt-get install -y git

# 克隆项目代码
RUN git clone https://github.com/yourusername/miracle-stock-analysis.git .

# 安装项目依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装中文字体
RUN apt-get install -y fonts-wqy-microhei

# 清理不必要的包
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 暴露端口5000供外部访问
EXPOSE 5000

# 运行应用
CMD ["flask", "run"]
