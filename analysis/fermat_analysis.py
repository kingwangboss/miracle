import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.signal import argrelextrema
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import io
import base64

# 设置中文字体
mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为黑体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题

class ComprehensiveAnalysis:
    def __init__(self, data):
        self.data = data

    def calculate_indicators(self):
        # 移动平均线
        for window in [5, 10, 20, 50]:
            self.data[f'MA{window}'] = self.data['Close'].rolling(window=window).mean()
        
        # RSI
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = self.data['Close'].ewm(span=12, adjust=False).mean()
        exp2 = self.data['Close'].ewm(span=26, adjust=False).mean()
        self.data['MACD'] = exp1 - exp2
        self.data['Signal'] = self.data['MACD'].ewm(span=9, adjust=False).mean()
        
        # Bollinger Bands
        self.data['BB_middle'] = self.data['Close'].rolling(window=20).mean()
        self.data['BB_upper'] = self.data['BB_middle'] + 2 * self.data['Close'].rolling(window=20).std()
        self.data['BB_lower'] = self.data['BB_middle'] - 2 * self.data['Close'].rolling(window=20).std()
        
        # 成交量变化率
        self.data['Volume_Change'] = self.data['Volume'].pct_change()

    def find_turning_points(self, window=10):
        self.calculate_indicators()
        
        # 只考虑所有指标都有效的数据点
        valid_data = self.data.dropna(subset=['Close', 'RSI', 'MACD', 'BB_upper', 'BB_lower', 'Signal'])
        
        max_idx = argrelextrema(valid_data['Close'].values, np.greater, order=window)[0]
        min_idx = argrelextrema(valid_data['Close'].values, np.less, order=window)[0]
        
        turning_points = []
        for idx in max_idx:
            if (valid_data['RSI'].iloc[idx] > 70 and 
                valid_data['Close'].iloc[idx] > valid_data['BB_upper'].iloc[idx] and
                valid_data['MACD'].iloc[idx] > valid_data['Signal'].iloc[idx]):
                turning_points.append((valid_data['Date'].iloc[idx], valid_data['Close'].iloc[idx], 'Peak'))
        for idx in min_idx:
            if (valid_data['RSI'].iloc[idx] < 30 and 
                valid_data['Close'].iloc[idx] < valid_data['BB_lower'].iloc[idx] and
                valid_data['MACD'].iloc[idx] < valid_data['Signal'].iloc[idx]):
                turning_points.append((valid_data['Date'].iloc[idx], valid_data['Close'].iloc[idx], 'Valley'))
        
        return turning_points

    def cluster_analysis(self):
        features = ['Close', 'RSI', 'MACD', 'Volume_Change']
        X = self.data[features].dropna()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # 创建一个新的 Series，索引为原始数据的索引，值为聚类结果
        cluster_series = pd.Series(clusters, index=X.index, name='Cluster')
        
        # 使用 concat 方法将聚类结果添加到原始数据中
        self.data = pd.concat([self.data, cluster_series], axis=1)

    def plot_results(self, turning_points):
        self.cluster_analysis()
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 20))
        
        # 价格和移动平均线
        ax1.plot(self.data['Date'], self.data['Close'], label='收盘价')
        for window in [5, 20, 50]:
            ax1.plot(self.data['Date'], self.data[f'MA{window}'], label=f'{window}日均线')
        
        peaks = [tp for tp in turning_points if tp[2] == 'Peak']
        valleys = [tp for tp in turning_points if tp[2] == 'Valley']
        
        ax1.scatter([p[0] for p in peaks], [p[1] for p in peaks], color='red', label='峰值')
        ax1.scatter([v[0] for v in valleys], [v[1] for v in valleys], color='green', label='谷值')
        
        ax1.set_title('股票价格与拐点分析')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('价格')
        ax1.legend()
        
        # RSI和MACD
        ax2.plot(self.data['Date'], self.data['RSI'], label='RSI')
        ax2.axhline(y=70, color='r', linestyle='--')
        ax2.axhline(y=30, color='g', linestyle='--')
        ax2.set_title('RSI指标')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('RSI值')
        ax2.legend()
        
        ax3.plot(self.data['Date'], self.data['MACD'], label='MACD')
        ax3.plot(self.data['Date'], self.data['Signal'], label='Signal')
        ax3.set_title('MACD指标')
        ax3.set_xlabel('日期')
        ax3.set_ylabel('MACD值')
        ax3.legend()
        
        plt.tight_layout()
        plt.show()
        
        # 聚类结果可视化
        plt.figure(figsize=(10, 6))
        valid_data = self.data.dropna(subset=['Close', 'RSI', 'Cluster'])
        scatter = plt.scatter(valid_data['Close'], valid_data['RSI'], c=valid_data['Cluster'], cmap='viridis')
        plt.colorbar(scatter)
        plt.title('价格-RSI聚类分析')
        plt.xlabel('收盘价')
        plt.ylabel('RSI')
        plt.show()

    def predict_next_turning_point(self):
        last_price = self.data['Close'].iloc[-1]
        last_rsi = self.data['RSI'].iloc[-1]
        last_macd = self.data['MACD'].iloc[-1]
        last_signal = self.data['Signal'].iloc[-1]
        last_bb_upper = self.data['BB_upper'].iloc[-1]
        last_bb_lower = self.data['BB_lower'].iloc[-1]
        last_volume_change = self.data['Volume_Change'].iloc[-1]
        
        peak_signals = (last_rsi > 70, last_price > last_bb_upper, last_macd > last_signal, last_volume_change > 0.1)
        valley_signals = (last_rsi < 30, last_price < last_bb_lower, last_macd < last_signal, last_volume_change < -0.1)
        
        peak_score = sum(peak_signals)
        valley_score = sum(valley_signals)
        
        if peak_score >= 3:
            return "多个指标显示可能即将出现峰值拐点,建议密切关注卖出机会"
        elif valley_score >= 3:
            return "多个指标显示可能即将出现谷值拐点,建议密切关注买入机会"
        else:
            return f"目前没有明确的拐点信号,建议继续观察。峰值信号强度: {peak_score}/4, 谷值信号强度: {valley_score}/4"

    def get_charts(self, turning_points):
        self.cluster_analysis()
        
        # 价格和移动平均线图表
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax1.plot(self.data['Date'], self.data['Close'], label='收盘价')
        for window in [5, 20, 50]:
            ax1.plot(self.data['Date'], self.data[f'MA{window}'], label=f'{window}日均线')
        
        peaks = [tp for tp in turning_points if tp[2] == 'Peak']
        valleys = [tp for tp in turning_points if tp[2] == 'Valley']
        
        ax1.scatter([p[0] for p in peaks], [p[1] for p in peaks], color='red', label='峰值')
        ax1.scatter([v[0] for v in valleys], [v[1] for v in valleys], color='green', label='谷值')
        
        ax1.set_title('股票价格与拐点分析')
        ax1.set_xlabel('日期')
        ax1.set_ylabel('价格')
        ax1.legend()
        plt.xticks(rotation=45)
        
        price_chart = self.fig_to_base64(fig)
        plt.close(fig)
        
        # RSI和MACD图表
        fig, (ax2, ax3) = plt.subplots(2, 1, figsize=(12, 10))
        ax2.plot(self.data['Date'], self.data['RSI'], label='RSI')
        ax2.axhline(y=70, color='r', linestyle='--')
        ax2.axhline(y=30, color='g', linestyle='--')
        ax2.set_title('RSI指标')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('RSI值')
        ax2.legend()
        
        ax3.plot(self.data['Date'], self.data['MACD'], label='MACD')
        ax3.plot(self.data['Date'], self.data['Signal'], label='Signal')
        ax3.set_title('MACD指标')
        ax3.set_xlabel('日期')
        ax3.set_ylabel('MACD值')
        ax3.legend()
        
        plt.tight_layout()
        indicators_chart = self.fig_to_base64(fig)
        plt.close(fig)
        
        # 聚类结果可视化
        fig, ax = plt.subplots(figsize=(10, 6))
        valid_data = self.data.dropna(subset=['Close', 'RSI', 'Cluster'])
        scatter = ax.scatter(valid_data['Close'], valid_data['RSI'], c=valid_data['Cluster'], cmap='viridis')
        plt.colorbar(scatter)
        ax.set_title('价格-RSI聚类分析')
        ax.set_xlabel('收盘价')
        ax.set_ylabel('RSI')
        
        cluster_chart = self.fig_to_base64(fig)
        plt.close(fig)
        
        return price_chart, indicators_chart, cluster_chart

    def fig_to_base64(self, fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')

# 使用示例
if __name__ == "__main__":
    from crawler.stock_crawler import StockCrawler
    
    crawler = StockCrawler("000001")
    data = crawler.fetch_data()
    
    analysis = ComprehensiveAnalysis(data)
    turning_points = analysis.find_turning_points()
    analysis.plot_results(turning_points)
    prediction = analysis.predict_next_turning_point()
    print(prediction)
