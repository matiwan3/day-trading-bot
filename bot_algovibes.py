# Script by Algovibes
# Resource: https://www.youtube.com/watch?v=Yi7tTKhN5TU
# Description: Fetch data from Bybit API using pybit library
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

# Trading parameters
DROP_THRESHOLD = 0.01 # 1% drop
TP_PERCENT = 0.004 # 0.4% take profit
SL_PERCENT = 0.002 # 0.2% stop loss
SYMBOL = "BTCUSD" 
QUANTITY = 0.01

client = HTTP(api_key=API_KEY, api_secret=API_SECRET)
current_time_ms = int(time.time() * 1000)
three_days_ago_ms = current_time_ms - 3 * 24 * 60 * 60 * 1000

response = client.get_kline(
    category='inverse', 
    symbol="BTCUSD", 
    interval=60, 
    start=three_days_ago_ms, 
    end=current_time_ms)

# print(response)

def process_kline_data(response):
    data = response["result"]["list"]
    
    df = pd.DataFrame(data, columns=["start_time", "open", "high", "low", "close", "volume", "turnover"])
    
    df["start_time"] = pd.to_datetime(df["start_time"], unit="ms")
    df.set_index("start_time", inplace=True)
    df = df.astype(float)
    df.columns = ["Open", "High", "Low", "Close", "Volume", "Turnover"]
    df = df.sort_index(ascending=True)
    return df

# df = process_kline_data(response)

# df.Close.plot()
# df["SMA"] = df["Close"].rolling(window=20).mean()
# df[['Close', 'SMA']].plot()
# print(df)
# plt.show()



def fetch_recent_data(client, symbol, interval=1, lookback_minutes=15):
    current_time_ms = int(time.time() * 1000)
    lookback_ms = lookback_minutes * 60 * 1000
    start_time_ms = current_time_ms - lookback_ms
    response = client.get_kline(
        category='linear', 
        symbol=symbol, 
        interval=interval, 
        start=start_time_ms, 
        end=current_time_ms
        )
    
    return process_kline_data(response)

# df = fetch_recent_data(client, SYMBOL)
# print(df)

def calc_move(df):
    start_price = df["Close"].iloc[0]
    end_price = df["Close"].iloc[-1]
    return start_price,end_price, (start_price / end_price - 1)

# calc_move(df)

def place_long_order(client, symbol, quantity, tp, sl):
    response = client.place_order(
        category='linear',
        symbol=symbol,
        side="Buy",
        order_type="Market",
        qty=quantity,
        time_in_force="GoodTillCancel",
        tp=tp,
        sl=sl
    )
    
    print(f"Long order placed: {response}")
    
    order = client.get_open_orders(
        category='linear',
        symbol=symbol,
        openOnly=1,
        limit=1)
    
    entry_price = float(order['result']['list'][0]['avgPrice'])
    
    tp_price = entry_price * (1 + tp)
    sl_price = entry_price * (1 - sl)
    
    modification_response = client.set_trading_stop(
        category='linear',
        symbol=symbol,
        take_profit=tp_price,
        stop_loss=sl_price,
        order_link_id=order['result']['list'][0]['orderLinkId']
    )
    
    print(f"Take-profit set at {tp_price}, stop-loss set at {sl_price}")
    
def get_position_status(client, symbol):
    response = client.get_positions(
        category="linear",
        symbol=symbol
    )
    
    position = response["result"]["list"][0]
    size = float(position["size"])
    side = position["side"]
    return {"size": size, "side": side}

# get_position_status(client, 'BTCUSD')

def run_bot():
    while True:
        df = fetch_recent_data(client, SYMBOL)
        start_price, end_price, move = calc_move(df)
        
        if move < -DROP_THRESHOLD:
            position = get_position_status(client, SYMBOL)
            
            if position["size"] == 0:
                place_long_order(client, SYMBOL, QUANTITY, TP_PERCENT, SL_PERCENT)
            else:
                print("Position already open")
                
        time.sleep(60)
        
def get_latest_price(client, symbol):
    response = client.get_tickers(
        category='linear',
        symbol=symbol
    )
    
    return response['result']['list'][0]['lastPrice']

print(f'Latest price: ', get_latest_price(client, 'OPUSDT'))