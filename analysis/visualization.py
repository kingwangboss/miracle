import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def get_charts(data, turning_points):
    # 创建子图
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.1,
                        subplot_titles=('股票价格与拐点分析', 'RSI指标', 'MACD指标'))
    
    # 价格和移动平均线
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name='收盘价'), row=1, col=1)
    for window in [5, 20, 50]:
        fig.add_trace(go.Scatter(x=data['Date'], y=data[f'MA{window}'], name=f'{window}日均线'), row=1, col=1)
    
    peaks = [tp for tp in turning_points if tp[2] == 'Peak']
    valleys = [tp for tp in turning_points if tp[2] == 'Valley']
    
    fig.add_trace(go.Scatter(x=[p[0] for p in peaks], y=[p[1] for p in peaks], mode='markers',
                             marker=dict(color='red', size=10), name='峰值'), row=1, col=1)
    fig.add_trace(go.Scatter(x=[v[0] for v in valleys], y=[v[1] for v in valleys], mode='markers',
                             marker=dict(color='green', size=10), name='谷值'), row=1, col=1)
    
    # RSI
    fig.add_trace(go.Scatter(x=data['Date'], y=data['RSI'], name='RSI'), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
    
    # MACD
    fig.add_trace(go.Scatter(x=data['Date'], y=data['MACD'], name='MACD'), row=3, col=1)
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Signal'], name='Signal'), row=3, col=1)
    
    fig.update_layout(
        height=600,
        title_text="股票分析图表",
        autosize=True,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(title_text="日期", row=3, col=1)
    fig.update_yaxes(title_text="价格", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    fig.update_yaxes(title_text="MACD", row=3, col=1)
    
    # 添加中文日期格式
    fig.update_traces(
        hovertemplate='%{x|%Y年%m月%d日}<br>%{y:.2f}',
        selector=dict(type='scatter')
    )
    
    price_chart = pio.to_json(fig)
    
    # 聚类分析
    cluster_chart = perform_cluster_analysis(data)
    
    return price_chart, cluster_chart

def perform_cluster_analysis(data):
    features = ['Close', 'RSI', 'MACD', 'Volume_Change']
    X = data[features].dropna()
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)
    
    cluster_fig = go.Figure()
    valid_data = data.dropna(subset=['Close', 'RSI', 'MACD', 'Volume_Change'])
    cluster_fig.add_trace(go.Scatter(x=valid_data['Close'], y=valid_data['RSI'], mode='markers',
                                     marker=dict(color=clusters, colorscale='Viridis', showscale=True),
                                     text=valid_data['Date'].dt.strftime('%Y年%m月%d日'), hoverinfo='text+x+y'))
    cluster_fig.update_layout(
        height=500,
        title='价格-RSI聚类分析', 
        xaxis_title='收盘价', 
        yaxis_title='RSI',
        autosize=True,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    return pio.to_json(cluster_fig)