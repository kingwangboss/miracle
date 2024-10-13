import requests
import pandas as pd
from datetime import datetime, timedelta

class StockCrawler:
    def __init__(self, stock_code):
        self.stock_code = stock_code
        self.base_url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"

    def fetch_data(self, days=365):
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
            raise ValueError(f"无法获取股票 {self.stock_code} 的数据")

        df = pd.DataFrame(
            [row.split(',') for row in data['data']['klines']],
            columns=['Date', 'Open', 'Close', 'High', 'Low', 'Volume', 'Amount', 'Amplitude', 'PctChg', 'Change', 'TurnoverRate']
        )

        df['Date'] = pd.to_datetime(df['Date'])  # 确保 'Date' 列是 datetime 类型
        for col in df.columns[1:]:
            df[col] = df[col].astype(float)

        return df.sort_values('Date')

# 使用示例
if __name__ == "__main__":
    crawler = StockCrawler("000001")  # 以平安银行为例
    data = crawler.fetch_data()
    print(data.head())
