from flask import Flask, render_template, request, jsonify
from crawler.stock_crawler import StockCrawler
from analysis.fermat_analysis import ComprehensiveAnalysis, configure_plt_for_backend
import concurrent.futures

app = Flask(__name__)

@app.before_request
def before_request():
    configure_plt_for_backend()

def process_stock_data(stock_input):
    try:
        crawler = StockCrawler(stock_input)
        data, stock_name, stock_code = crawler.fetch_data()
        
        analysis = ComprehensiveAnalysis(data)
        accurate_points = analysis.find_accurate_turning_points()
        price_chart, cluster_chart = analysis.get_charts(accurate_points)
        prediction = analysis.predict_next_turning_point()
        
        return accurate_points, price_chart, cluster_chart, prediction, stock_name, stock_code
    except ValueError as e:
        return str(e), None, None, None, None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        stock_input = request.form['stock_input']
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(process_stock_data, stock_input)
            result = future.result()
        
        if isinstance(result[0], str):  # 错误情况
            return jsonify({'error': result[0]}), 400
        
        accurate_points, price_chart, cluster_chart, prediction, stock_name, stock_code = result
        
        return jsonify({
            'stock_name': stock_name,
            'stock_code': stock_code,
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
