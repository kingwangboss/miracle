import requests
import pandas as pd
from datetime import datetime, timedelta
import re
import json

class StockCrawler:
    def __init__(self, stock_input):
        self.stock_input = stock_input
        self.base_url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
        self.search_url = "https://searchapi.eastmoney.com/api/suggest/get"
        self.stock_name = None  # 添加这行
        self.stock_code = None  # 添加这行

    @staticmethod
    def is_valid_stock_code(stock_code):
        return re.match(r'^[0-9]{6}$', stock_code) is not None

    def search_stock_code(self):
        params = {
            "input": self.stock_input,
            "type": "14",
            "token": "D43BF722C8E33BDC906FB84D85E326E8",
            "count": "1"
        }
        response = requests.get(self.search_url, params=params)
        data = response.json()
        
        if data['QuotationCodeTable']['Data']:
            self.stock_code = data['QuotationCodeTable']['Data'][0]['Code']
            self.stock_name = data['QuotationCodeTable']['Data'][0]['Name']  # 添加这行
            return self.stock_code
        else:
            raise ValueError(f"无法找到股票: {self.stock_input}")

    def fetch_data(self, days=365):
        if self.is_valid_stock_code(self.stock_input):
            self.stock_code = self.stock_input
            self.search_stock_code()  # 获取股票名称
        else:
            self.search_stock_code()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            "secid": f"1.{self.stock_code}" if self.stock_code.startswith('6') else f"0.{self.stock_code}",
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",  # 日线数据
            "fqt": "0",    # 不复权
            "beg": start_date.strftime("%Y%m%d"),
            "end": end_date.strftime("%Y%m%d"),
            "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            "rtntype": "6",
        }

        response = requests.get(self.base_url, params=params)
        data = response.json()

        if data['data'] is None:
            raise ValueError(f"无法获取股票 {self.stock_code} 的数据，请确认股票代码是否正确")

        df = pd.DataFrame(
            [row.split(',') for row in data['data']['klines']],
            columns=['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Amplitude', 'PctChg', 'Change', 'TurnoverRate']
        )

        df['Date'] = pd.to_datetime(df['Date'])  # 确保 'Date' 列是 datetime 类型
        for col in df.columns[1:]:
            df[col] = df[col].astype(float)

        return df.sort_values('Date'), self.stock_name, self.stock_code  # 修改这行

# 使用示例
if __name__ == "__main__":
    crawler = StockCrawler("平安银行")  # 可以使用股票名称
    data, stock_name, stock_code = crawler.fetch_data()
    print(data.head())
    print(f"股票名称: {stock_name}, 股票代码: {stock_code}")
