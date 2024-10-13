from flask import Flask, render_template, request, jsonify
from crawler.stock_crawler import StockCrawler
from analysis.fermat_analysis import ComprehensiveAnalysis, configure_plt_for_backend
import io
import base64
from threading import Lock

app = Flask(__name__)
analysis_lock = Lock()

@app.before_request
def before_request():
    configure_plt_for_backend()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock_code = request.form['stock_code']
        crawler = StockCrawler(stock_code)
        data = crawler.fetch_data()
        
        with analysis_lock:
            configure_plt_for_backend()
            analysis = ComprehensiveAnalysis(data)
            accurate_points = analysis.find_accurate_turning_points()
            price_chart, cluster_chart = analysis.get_charts(accurate_points)
            prediction = analysis.predict_next_turning_point()
        
        return jsonify({
            'turning_points': [
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'price': float(price),
                    'type': point_type
                } for date, price, point_type in accurate_points
            ],
            'price_chart': price_chart,
            'cluster_chart': cluster_chart,
            'prediction': prediction
        })
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
