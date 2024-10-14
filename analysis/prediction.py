import numpy as np
from datetime import timedelta
from sklearn.linear_model import LinearRegression

def predict_next_turning_point(data, turning_points):
    if not turning_points:
        return "无法识别准确的拐点，可能需要更多数据。"

    last_point = turning_points[-1]
    last_price = data['Close'].iloc[-1]
    last_date = data['Date'].iloc[-1]
    
    # 计算最近30天的趋势
    recent_data = data.tail(30)
    X = np.array(range(len(recent_data))).reshape(-1, 1)
    y = recent_data['Close'].values
    model = LinearRegression()
    model.fit(X, y)
    trend = model.coef_[0]

    # 计算拐点可能性得分
    turning_point_score = calculate_turning_point_score(data, -1, trend)

    # 计算距离上一个拐点的天数
    days_since_last_point = (last_date - last_point[0]).days

    # 根据距离上一个拐点的天数调整得分
    if days_since_last_point < 7:
        turning_point_score *= (days_since_last_point / 7)
    elif days_since_last_point > 30:
        turning_point_score *= 1.5

    # 使用sigmoid函数将得分映射到(0, 1)区间
    turning_point_probability = 1 / (1 + np.exp(-turning_point_score))

    # 预测未来7-15天内出现拐点的可能性
    days_to_turning_point = int(7 + (1 - turning_point_probability) * 8)
    predicted_date = last_date + timedelta(days=days_to_turning_point)

    trend_direction = "上升" if trend > 0 else "下降"
    
    # 考虑最近的拐点类型
    if last_point[2] == 'Peak':
        turning_point_type = "谷值" if trend < 0 else "可能的新高点"
    else:  # Valley
        turning_point_type = "峰值" if trend > 0 else "可能的新低点"
    
    prediction = f"当前趋势：{trend_direction}\n"
    prediction += f"预计拐点：{predicted_date.strftime('%Y-%m-%d')}（{days_to_turning_point}天后）\n"
    prediction += f"拐点类型：{turning_point_type}\n"
    prediction += f"出现可能性：{turning_point_probability:.2%}\n"
    prediction += "建议："
    
    if turning_point_probability > 0.7:
        if trend > 0 and last_point[2] == 'Valley':
            prediction += "股价可能接近高点，考虑逐步减仓或设置止盈"
        elif trend < 0 and last_point[2] == 'Peak':
            prediction += "股价可能接近低点，考虑逐步建仓或观望"
        else:
            prediction += "当前趋势强劲，但可能即将出现拐点，密切关注市场变化"
    elif turning_point_probability > 0.4:
        prediction += "市场可能即将出现变化，保持观望，密切关注市场动向"
    else:
        if trend > 0:
            prediction += "短期可能继续上涨，可考虑持有或小幅加仓，但注意设置止盈"
        else:
            prediction += "短期可能继续下跌，可考虑观望或小幅减仓，但注意把握反弹机会"

    return prediction