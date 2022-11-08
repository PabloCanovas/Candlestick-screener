import os
import yfinance as yf
import pandas as pd
import talib
from datetime import datetime, timedelta
from flask import Flask, render_template, request
from patterns import patterns

app = Flask(__name__)

@app.route("/")
def index():
    pattern = request.args.get('pattern', None)

    stocks_df = pd.read_csv('datasets/companies.csv', header=None)
    stocks_df = stocks_df.rename(columns={0: "symbol", 1:"company"})
    stocks = dict(zip(stocks_df.symbol, [""] * len(stocks_df.symbol)))

    for key, value in stocks.items(): 
        stocks[key] = {}

    if pattern:
        filenames = os.listdir('datasets/daily')
        for filename in filenames:
            df = pd.read_csv(f'datasets/daily/{filename}')
            pattern_function = getattr(talib, pattern)

            symbol = filename.split('.')[0]
            try:
                result = pattern_function(df['Open'], df['High'], df['Low'], df['Close'])
                last = result.tail(1).values[0]

                if last > 0:
                    stocks[symbol][pattern] = 'bullish'
                elif last < 0:
                    stocks[symbol][pattern] = 'bearish'
                else:
                    stocks[symbol][pattern] = None

                if last != 0:
                    print(symbol + ": " + stocks[symbol][pattern])
            except:
                pass

    return render_template('index.html', patterns=patterns, stocks=stocks, current_pattern=pattern)


@app.route("/snapshot")
def snapshot():
    with open('datasets/companies.csv') as f:
        companies = f.read().splitlines()
        for company in companies:
            symbol = company.split(',')[0]
            last_trading_day = get_last_trading_day(datetime.today()).strftime("%Y-%m-%d")
            
            # df = yf.download(symbol, start='2022-01-01',end='2022-11-04').reset_index()
            df = yf.download(symbol, start=last_trading_day).reset_index()
            df['Date'] = (pd.to_datetime(df['Date'], format = "%Y-%m-%d")).astype(str)
            
            all_data = pd.read_csv(f'datasets/daily/{symbol}')
            all_data = pd.concat([all_data, df])

            all_data.to_csv(f'datasets/daily/{symbol}', index=False)

        return 'OK'


def is_weekday(date):
    if date.weekday() in [5,6]:
        return False
    else:
        return True

def get_last_trading_day(date):
    if is_weekday(date):
        return date
    else:
         return get_last_trading_day(date - timedelta(days=1))
