import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib as mpl
from scipy.signal import argrelextrema
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import io
import base64
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# 设置中文字体
mpl.rcParams['font.sans-serif'] = ['SimHei']  # 指定默认字体为黑体
mpl.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题

# 在文件开头添加以下函数
def configure_plt_for_backend():
    plt.switch_backend('Agg')

class ComprehensiveAnalysis:
    def __init__(self, data):
        self.data = data
        configure_plt_for_backend()

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

    def fermat_turning_points(self, window=5):
        prices = self.data['Close'].values
        turning_points = []
        
        for i in range(window, len(prices) - window):
            left = prices[i-window:i]
            right = prices[i:i+window+1]
            
            if np.all(left <= prices[i]) and np.all(right <= prices[i]):
                turning_points.append((self.data['Date'].iloc[i], prices[i], 'Peak'))
            elif np.all(left >= prices[i]) and np.all(right >= prices[i]):
                turning_points.append((self.data['Date'].iloc[i], prices[i], 'Valley'))
        
        return turning_points

    def find_accurate_turning_points(self, window=5):
        self.calculate_indicators()
        prices = self.data['Close'].values
        turning_points = []
        
        for i in range(window, len(prices) - window):
            left = prices[i-window:i]
            right = prices[i:i+window+1]
            
            if np.all(left <= prices[i]) and np.all(right <= prices[i]):
                # 潜在峰值
                if (self.data['RSI'].iloc[i] > 60 or  # 放宽RSI条件
                    prices[i] > self.data['BB_upper'].iloc[i] or
                    self.data['MACD'].iloc[i] > self.data['Signal'].iloc[i]):
                    turning_points.append((self.data['Date'].iloc[i], prices[i], 'Peak'))
            elif np.all(left >= prices[i]) and np.all(right >= prices[i]):
                # 潜在谷值
                if (self.data['RSI'].iloc[i] < 40 or  # 放宽RSI条件
                    prices[i] < self.data['BB_lower'].iloc[i] or
                    self.data['MACD'].iloc[i] < self.data['Signal'].iloc[i]):
                    turning_points.append((self.data['Date'].iloc[i], prices[i], 'Valley'))
        
        return turning_points

    def get_charts(self, turning_points):
        self.cluster_analysis()
        
        # 创建子图
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                            subplot_titles=('股票价格与拐点分析', 'RSI指标', 'MACD指标'))
        
        # 价格和移动平均线
        fig.add_trace(go.Scatter(x=self.data['Date'], y=self.data['Close'], name='收盘价'), row=1, col=1)
        for window in [5, 20, 50]:
            fig.add_trace(go.Scatter(x=self.data['Date'], y=self.data[f'MA{window}'], name=f'{window}日均线'), row=1, col=1)
        
        peaks = [tp for tp in turning_points if tp[2] == 'Peak']
        valleys = [tp for tp in turning_points if tp[2] == 'Valley']
        
        fig.add_trace(go.Scatter(x=[p[0] for p in peaks], y=[p[1] for p in peaks], mode='markers',
                                 marker=dict(color='red', size=10), name='峰值'), row=1, col=1)
        fig.add_trace(go.Scatter(x=[v[0] for v in valleys], y=[v[1] for v in valleys], mode='markers',
                                 marker=dict(color='green', size=10), name='谷值'), row=1, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(x=self.data['Date'], y=self.data['RSI'], name='RSI'), row=2, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        fig.add_trace(go.Scatter(x=self.data['Date'], y=self.data['MACD'], name='MACD'), row=3, col=1)
        fig.add_trace(go.Scatter(x=self.data['Date'], y=self.data['Signal'], name='Signal'), row=3, col=1)
        
        fig.update_layout(
            height=600,  # 调整高度
            title_text="股票分析图表",
            autosize=True,
            margin=dict(l=50, r=50, t=50, b=50),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig.update_xaxes(title_text="日期", row=3, col=1)
        fig.update_yaxes(title_text="价格", row=1, col=1)
        fig.update_yaxes(title_text="RSI", row=2, col=1)
        fig.update_yaxes(title_text="MACD", row=3, col=1)
        
        price_chart = pio.to_json(fig)
        
        # 聚类结果可视化
        cluster_fig = go.Figure()
        valid_data = self.data.dropna(subset=['Close', 'RSI', 'Cluster'])
        cluster_fig.add_trace(go.Scatter(x=valid_data['Close'], y=valid_data['RSI'], mode='markers',
                                         marker=dict(color=valid_data['Cluster'], colorscale='Viridis', showscale=True),
                                         text=valid_data['Date'], hoverinfo='text+x+y'))
        cluster_fig.update_layout(
            height=500,  # 调整高度
            title='价格-RSI聚类分析', 
            xaxis_title='收盘价', 
            yaxis_title='RSI',
            autosize=True,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        cluster_chart = pio.to_json(cluster_fig)
        
        return price_chart, cluster_chart

    def fig_to_base64(self, fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def predict_next_turning_point(self):
        accurate_points = self.find_accurate_turning_points()
        if not accurate_points:
            return "无法识别准确的拐点，可能需要更多数据。"

        last_point = accurate_points[-1]
        last_price = self.data['Close'].iloc[-1]
        last_date = self.data['Date'].iloc[-1]
        last_rsi = self.data['RSI'].iloc[-1]
        last_macd = self.data['MACD'].iloc[-1]
        last_signal = self.data['Signal'].iloc[-1]
        last_bb_upper = self.data['BB_upper'].iloc[-1]
        last_bb_lower = self.data['BB_lower'].iloc[-1]

        days_since_last_point = (last_date - last_point[0]).days
        price_change = (last_price - last_point[1]) / last_point[1] * 100

        buy_signals = [
            price_change < -3,  # 放宽价格变化条件
            last_rsi < 40,      # 放宽RSI条件
            last_price < last_bb_lower,
            last_macd < last_signal
        ]

        sell_signals = [
            price_change > 3,   # 放宽价格变化条件
            last_rsi > 60,      # 放宽RSI条件
            last_price > last_bb_upper,
            last_macd > last_signal
        ]

        buy_score = sum(buy_signals)
        sell_score = sum(sell_signals)

        if last_point[2] == 'Peak':
            if buy_score >= 2:  # 降低买入信号阈值
                return f"最近的拐点是{days_since_last_point}天前的峰值。当前价格已下跌{abs(price_change):.2f}%，多个技术指标显示可能接近谷值，建议考虑买入。"
            elif sell_score >= 2:  # 降低卖出信号阈值
                return f"最近的拐点是{days_since_last_point}天前的峰值。当前价格已上涨{price_change:.2f}%，多个技术指标显示可能形成新的峰值，建议考虑卖出。"
            else:
                return f"最���的拐点是{days_since_last_point}天前的峰值。技术指标显示混合信号，建议观望。"
        else:  # Valley
            if sell_score >= 2:  # 降低卖出信号阈值
                return f"最近的拐点是{days_since_last_point}天前的谷值。当前价格已上涨{price_change:.2f}%，多个技术指标显示可能接近峰值，建议考虑卖出。"
            elif buy_score >= 2:  # 降低买入信号阈值
                return f"最近的拐点是{days_since_last_point}天前的谷值。当前价格已下跌{abs(price_change):.2f}%，多个技术指标显示可能形成新的谷值，建议考虑买入。"
            else:
                return f"最近的拐点是{days_since_last_point}天前的谷值。技术指标显示混合信号，建议观望。"

# 使用示例
if __name__ == "__main__":
    from crawler.stock_crawler import StockCrawler
    
    crawler = StockCrawler("000001")
    data = crawler.fetch_data()
    
    analysis = ComprehensiveAnalysis(data)
    accurate_points = analysis.find_accurate_turning_points()
    price_chart, cluster_chart = analysis.get_charts(accurate_points)
    prediction = analysis.predict_next_turning_point()
    print(prediction)