from flask import Flask, render_template, request, jsonify
from crawler.stock_crawler import StockCrawler
from analysis import ComprehensiveAnalysis
import concurrent.futures

app = Flask(__name__)

def process_stock_data(stock_input):
    try:
        crawler = StockCrawler(stock_input)
        data, stock_name, stock_code = crawler.fetch_data()
        
        analysis = ComprehensiveAnalysis(data)
        turning_points, price_chart, cluster_chart, prediction = analysis.analyze()
        
        return turning_points, price_chart, cluster_chart, prediction, stock_name, stock_code
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
        
        turning_points, price_chart, cluster_chart, prediction, stock_name, stock_code = result
        
        return jsonify({
            'stock_name': stock_name,
            'stock_code': stock_code,
            'turning_points': [
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'price': float(price),
                    'type': point_type
                } for date, price, point_type in turning_points
            ],
            'price_chart': price_chart,
            'cluster_chart': cluster_chart,
            'prediction': prediction
        })
    
    return render_template('index.html')

@app.route('/api/v1/analyze', methods=['GET'])
def analyze_stock():
    """
    API接口，通过股票代码或名称获取分析结果
    请求参数：
    - stock: 股票代码或名称（必需）
    - charts: 是否返回图表数据（可选，默认False）
    
    示例：
    GET /api/v1/analyze?stock=平安银行&charts=true
    """
    stock_input = request.args.get('stock')
    include_charts = request.args.get('charts', 'false').lower() == 'true'
    
    if not stock_input:
        return jsonify({
            'error': '请提供股票代码或名称',
            'code': 400
        }), 400
    
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(process_stock_data, stock_input)
            result = future.result()
        
        if isinstance(result[0], str):  # 错误情况
            return jsonify({
                'error': result[0],
                'code': 400
            }), 400
        
        turning_points, price_chart, cluster_chart, prediction, stock_name, stock_code = result
        
        response = {
            'code': 200,
            'data': {
                'stock_name': stock_name,
                'stock_code': stock_code,
                'turning_points': [
                    {
                        'date': date.strftime('%Y-%m-%d'),
                        'price': float(price),
                        'type': point_type
                    } for date, price, point_type in turning_points
                ],
                'prediction': prediction
            }
        }
        
        if include_charts:
            response['data']['charts'] = {
                'price_chart': price_chart,
                'cluster_chart': cluster_chart
            }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            'error': f'分析过程中发生错误: {str(e)}',
            'code': 500
        }), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
