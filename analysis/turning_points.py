import numpy as np

def find_accurate_turning_points(data, window=5, min_distance=5, threshold=0.2):
    prices = data['Close'].values
    turning_points = []
    last_point_index = -min_distance
    last_point_type = None
    
    for i in range(window, len(prices) - window):
        left = prices[i-window:i]
        right = prices[i:i+window+1]
        
        # 计算局部趋势
        local_data = np.concatenate([left, [prices[i]], right])
        local_trend = np.polyfit(range(len(local_data)), local_data, 1)[0]
        
        # 计算拐点可能性得分
        turning_point_score = calculate_turning_point_score(data, i, local_trend)
        
        is_peak = np.all(left <= prices[i]) and np.all(right <= prices[i])
        is_valley = np.all(left >= prices[i]) and np.all(right >= prices[i])
        
        if (is_peak or is_valley) and turning_point_score > threshold and (i - last_point_index) >= min_distance:
            point_type = 'Peak' if is_peak else 'Valley'
            
            if point_type != last_point_type or last_point_type is None:
                if not turning_points or \
                   (point_type == 'Peak' and prices[i] > turning_points[-1][1]) or \
                   (point_type == 'Valley' and prices[i] < turning_points[-1][1]):
                    turning_points.append((data['Date'].iloc[i], prices[i], point_type))
                    last_point_index = i
                    last_point_type = point_type
            elif (point_type == 'Peak' and prices[i] > turning_points[-1][1]) or \
                 (point_type == 'Valley' and prices[i] < turning_points[-1][1]):
                turning_points[-1] = (data['Date'].iloc[i], prices[i], point_type)
                last_point_index = i
    
    return turning_points

def calculate_turning_point_score(data, i, local_trend):
    rsi = data['RSI'].iloc[i]
    macd = data['MACD'].iloc[i]
    signal = data['Signal'].iloc[i]
    bb_upper = data['BB_upper'].iloc[i]
    bb_lower = data['BB_lower'].iloc[i]
    k = data['K'].iloc[i]
    d = data['D'].iloc[i]
    price = data['Close'].iloc[i]
    
    turning_point_score = 0
    if local_trend > 0:  # 上升趋势
        turning_point_score += (rsi - 50) / 50 if rsi > 50 else 0
        turning_point_score += (price - bb_upper) / (bb_upper - bb_lower) if price > bb_upper else 0
        turning_point_score += (macd - signal) / abs(signal) if macd > signal else 0
        turning_point_score += (k - d) / 100 if k > d else 0
    else:  # 下降趋势
        turning_point_score += (50 - rsi) / 50 if rsi < 50 else 0
        turning_point_score += (bb_lower - price) / (bb_upper - bb_lower) if price < bb_lower else 0
        turning_point_score += (signal - macd) / abs(signal) if macd < signal else 0
        turning_point_score += (d - k) / 100 if k < d else 0
    
    return max(min(turning_point_score, 1), 0.1)
