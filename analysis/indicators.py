import pandas as pd
import numpy as np

def calculate_indicators(data):
    # 移动平均线
    for window in [5, 10, 20, 50]:
        data[f'MA{window}'] = data['Close'].rolling(window=window).mean()
    
    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = data['Close'].ewm(span=12, adjust=False).mean()
    exp2 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = exp1 - exp2
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    # Bollinger Bands
    data['BB_middle'] = data['Close'].rolling(window=20).mean()
    data['BB_upper'] = data['BB_middle'] + 2 * data['Close'].rolling(window=20).std()
    data['BB_lower'] = data['BB_middle'] - 2 * data['Close'].rolling(window=20).std()
    
    # 成交量变化率
    data['Volume_Change'] = data['Volume'].pct_change()
    
    # KDJ指标
    low_list = data['Low'].rolling(window=9, min_periods=9).min()
    high_list = data['High'].rolling(window=9, min_periods=9).max()
    rsv = (data['Close'] - low_list) / (high_list - low_list) * 100
    data['K'] = rsv.ewm(com=2).mean()
    data['D'] = data['K'].ewm(com=2).mean()
    data['J'] = 3 * data['K'] - 2 * data['D']

    # OBV指标
    data['OBV'] = (data['Close'].diff().apply(lambda x: 1 if x > 0 else (-1 if x < 0 else 0)) * data['Volume']).cumsum()

    return data
