from .indicators import calculate_indicators
from .turning_points import find_accurate_turning_points
from .prediction import predict_next_turning_point
from .visualization import get_charts

class ComprehensiveAnalysis:
    def __init__(self, data):
        self.data = data
        self.data = calculate_indicators(self.data)

    def analyze(self):
        turning_points = find_accurate_turning_points(self.data)
        price_chart, cluster_chart = get_charts(self.data, turning_points)
        prediction = predict_next_turning_point(self.data, turning_points)
        return turning_points, price_chart, cluster_chart, prediction
