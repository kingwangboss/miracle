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

## 本地运行

1. 克隆项目到本地:   ```
   git clone https://github.com/yourusername/miracle-stock-analysis.git
   cd miracle-stock-analysis   ```

2. 安装依赖:   ```
   pip install -r requirements.txt   ```

3. 运行Web应用:   ```
   python app.py   ```

4. 在浏览器中打开 `http://localhost:5000`

5. 在输入框中输入6位股票代码(例如: 000001),点击"分析"按钮。

## Docker部署

本应用可以通过Docker在Linux环境下轻松部署。

1. 确保您的Linux服务器已安装Docker。如果没有，可以使用以下命令安装：   ```
   sudo apt-get update
   sudo apt-get install docker.io   ```

2. 克隆项目到本地：   ```
   git clone https://github.com/yourusername/miracle-stock-analysis.git
   cd miracle-stock-analysis   ```

3. 构建Docker镜像：   ```
   sudo docker build -t miracle-stock-analysis .
   ```

4. 运行Docker容器：   ```
   sudo docker run -d -p 5000:5000 miracle-stock-analysis
   ```

5. 现在，您可以通过服务器的IP地址和端口5000来访问应用，例如：   ```
   http://your_server_ip:5000
   ```

注意：请确保您的服务器防火墙允许5000端口的访问。如果您使用的是云服务器，可能还需要在云平台的安全组设置中开放5000端口。

## 注意事项

- 本工具仅供学习和研究使用,不构成任何投资建议。
- 股市有风险,投资需谨慎。请在使用本工具进行实际投资决策时,结合其他分析方法和市场信息。
- 由于数据来源和市场的复杂性,分析结果可能存在误差,请谨慎使用。

## 贡献

欢迎提出问题、建议或直接贡献代码来改进这个项目。请通过GitHub Issues或Pull Requests与我们互动。

## 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。
