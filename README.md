# Miracle 股票分析工具

Miracle 是一个基于Python的股票分析工具,利用多种技术指标和机器学习方法来识别股票价格的潜在拐点并进行预测。

## 功能特点

1. 数据爬取: 自动从东方财富网获取指定股票的历史数据。
2. 技术指标分析: 计算并分析多个技术指标,包括移动平均线、RSI、MACD和布林带。
3. 拐点识别: 使用改进的费马引理结合多个技术指标来识别潜在的价格拐点。
4. 聚类分析: 使用K-means算法对股票数据进行聚类,以识别不同的市场状态。
5. 可视化: 生成价格走势图、技术指标图和聚类分析图。
6. 拐点预测: 基于当前市场状态预测可能出现的下一个拐点。
7. Web界面: 提供简单的Web界面,方便用户输入股票代码并查看分析结果。

## 使用方法

1. 安装依赖:   ```
   pip install -r requirements.txt   ```

2. 运行Web应用:   ```
   python app.py   ```

3. 在浏览器中打开 `http://localhost:5000`

4. 在输入框中输入6位股票代码(例如: 000001),点击"分析"按钮。

5. 等待分析完成,查看结果,包括:
   - 识别出的拐点列表
   - 价格走势和拐点分析图
   - 技术指标(RSI和MACD)分析图
   - 聚类分析图
   - 下一个可能拐点的预测结果

## 计算逻辑

1. 数据获取:
   - 使用东方财富网的API获取指定股票的历史数据。
   - 默认获取最近一年的日线数据。

2. 技术指标计算:
   - 移动平均线(MA): 计算5日、10日、20日和50日移动平均线。
   - 相对强弱指标(RSI): 使用14天周期计算RSI。
   - MACD: 计算12日和26日EMA,以及9日信号线。
   - 布林带: 计算20日移动平均线及其上下2个标准差。

3. 拐点识别:
   - 使用scipy的argrelextrema函数找出局部最大值和最小值。
   - 结合RSI、布林带和MACD指标进行确认。
   - 峰值条件: RSI > 70, 价格 > 布林带上轨, MACD > 信号线。
   - 谷值条件: RSI < 30, 价格 < 布林带下轨, MACD < 信号线。

4. 聚类分析:
   - 使用收盘价、RSI、MACD和成交量变化率作为特征。
   - 应用K-means算法,将数据点分为3类。

5. 拐点预测:
   - 分析最新的市场状态,包括RSI、布林带位置、MACD和成交量变化。
   - 根据多个指标的组合给出可能出现拐点的预警。

## 注意事项

- 本工具仅供学习和研究使用,不构成任何投资建议。
- 股市有风险,投资需谨慎。请在使用本工具进行实际投资决策时,结合其他分析方法和市场信息。
- 由于数据来源和市场的复杂性,分析结果可能存在误差,请谨慎使用。

## 贡献

欢迎提出问题、建议或直接贡献代码来改进这个项目。请通过GitHub Issues或Pull Requests与我们互动。

## 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## Docker部署

本应用可以通过Docker轻松部署，无需手动克隆代码或安装依赖。

1. 确保您的系统已安装Docker。

2. 创建一个新文件夹，并在其中创建名为`Dockerfile`的文件，将以下内容复制到这个文件中：
   ```dockerfile
   # 使用官方Python运行时作为父镜像
   FROM python:3.9-slim

   # 安装git
   RUN apt-get update && apt-get install -y git

   # 设置工作目录
   WORKDIR /app

   # 克隆项目代码
   RUN git clone https://github.com/kingwangboss/miracle.git .

   # 安装项目依赖
   RUN pip install --no-cache-dir -r requirements.txt

   # 安装中文字体
   RUN apt-get install -y fonts-wqy-microhei && apt-get clean && rm -rf /var/lib/apt/lists/*

   # 设置环境变量
   ENV FLASK_APP=app.py
   ENV FLASK_RUN_HOST=0.0.0.0

   # 暴露端口5000供外部访问
   EXPOSE 5000

   # 运行应用
   CMD ["flask", "run"]
   ```

   注意：请将 `https://github.com/yourusername/miracle-stock-analysis.git` 替换为实际的 GitHub 仓库 URL。

3. 在包含Dockerfile的文件夹中运行以下命令来构建Docker镜像：   ```
   docker build -t miracle-stock-analysis .
   ```

4. 构建完成后，运行以下命令来启动应用：   ```
   docker run -p 5000:5000 miracle-stock-analysis
   ```

5. 在浏览器中访问 `http://localhost:5000` 来使用应用。

注意: 如果您在远程服务器上运行Docker容器，请将`localhost`替换为服务器的IP地址或域名。
