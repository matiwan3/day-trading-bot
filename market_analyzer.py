import os
import requests
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import pandas as pd
from pybit.unified_trading import HTTP
import time

# Load API keys from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
coin_pairs = ["OPUSDT", "SOLUSDT", "BTCUSDT", "ETHUSDT"]
lookback = 1440; # 1440 minutes = 1 day | 15 minutes = 15 minutes | 60 minutes = 1 hour 

client = HTTP(api_key=API_KEY, api_secret=API_SECRET)

def get_latest_price(client, symbol):
    response = client.get_tickers(
        category='linear',
        symbol=symbol
    )
    
    return response['result']['list'][0]['lastPrice']

def get_raw_response(client, symbol, interval=1):
    current_time_ms = int(time.time() * 1000)
    three_days_ago_ms = current_time_ms - 3 * 24 * 60 * 60 * 1000
    response = client.get_kline(
        category='linear', 
        symbol=symbol, 
        interval=interval, 
        start=three_days_ago_ms, 
        end=current_time_ms)
    
    return response    

# print(get_raw_response(client, "BTCUSDT"))

def lookback_change(client, symbol, lookback_minutes=15,interval=1, ):
    current_time_ms = int(time.time() * 1000)
    lookback_ms = lookback_minutes * 60 * 1000
    start_time_ms = current_time_ms - lookback_ms
    response = client.get_kline(
        category='linear', 
        symbol=symbol, 
        interval=interval, 
        start=start_time_ms, 
        end=current_time_ms)
    
    if 'result' in response and 'list' in response['result'] and len(response['result']['list']) > 0:
        open_price = float(response['result']['list'][0][1])
        close_price = float(response['result']['list'][-1][4])
        percentage_change = ((close_price - open_price) / open_price) * 100
        return percentage_change
    else:
        return None

def print_coins_data():
    for coin in coin_pairs:
        print(f'Latest price for {coin}: ', get_latest_price(client, coin))
        print(f'{lookback} minute change for {coin}: ', lookback_change(client, coin, lookback))
        print('\n')
        
print_coins_data()
