from flask import Flask, render_template, request, jsonify
from crawler.stock_crawler import StockCrawler
from analysis.fermat_analysis import ComprehensiveAnalysis
import io
import base64

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock_code = request.form['stock_code']
        crawler = StockCrawler(stock_code)
        data = crawler.fetch_data()
        
        analysis = ComprehensiveAnalysis(data)
        turning_points = analysis.find_turning_points()
        
        # 获取图表
        price_chart, indicators_chart, cluster_chart = analysis.get_charts(turning_points)
        
        prediction = analysis.predict_next_turning_point()
        
        return jsonify({
            'turning_points': [
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'price': float(price),
                    'type': point_type
                } for date, price, point_type in turning_points
            ],
            'price_chart': price_chart,
            'indicators_chart': indicators_chart,
            'cluster_chart': cluster_chart,
            'prediction': prediction
        })
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
