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

df = process_kline_data(response)

df.Close.plot()
df["SMA"] = df["Close"].rolling(window=20).mean()
df[['Close', 'SMA']].plot()

print(df)
plt.show()