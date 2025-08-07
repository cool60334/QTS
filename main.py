import asyncio
import logging
import colorlog
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict

from cybotrade.strategy import Strategy as BaseStrategy
from cybotrade.models import RuntimeConfig, RuntimeMode
from cybotrade.permutation import Permutation

API_KEY = "1zXqMAnZuEQtG8U9CEUmoXZTlaEVVcF57nmel0hhBseWbNCs"
API_SECRET = "x093SBPdN1JWvKurJkc0UJeH56ZOgy4bNwOopXm4IATVhw08pYe6p7WjDc7EB9dw1fJsaGW2"

START_TIME = datetime(2020, 6, 1, 0, 0, 0, tzinfo=timezone.utc)
ts_start_time = int(START_TIME.timestamp()*1000)
END_TIME = datetime(2020, 11, 30, 0, 0, 0, tzinfo=timezone.utc)
ts_end_time = int(END_TIME.timestamp()*1000)

FILE_NAME = "test.csv"

# DATASOURCE_TOPIC = f"coinglass|1m|futures/globalLongShortAccountRatio/history?exchange=Binance&symbol=BTCUSDT&interval=1h&startTime={ts_start_time}&endTime={ts_end_time}&limit=4500"
DATASOURCE_TOPIC = f"coinglass|1m|futures/openInterest/ohlc-history"
CANDLE_TOPIC = "candles-5m-BTC/USDT-bybit"

# class Strategy(BaseStrategy):
#     data = []
    
#     def __init__(self):
#         handler = colorlog.StreamHandler()
#         handler.setFormatter(
#             colorlog.ColoredFormatter(f"%(log_color)s{Strategy.LOG_FORMAT}")
#         )
#         file_handler = logging.FileHandler("test-datamap.log")
#         file_handler.setLevel(logging.DEBUG)
#         super().__init__(log_level=logging.DEBUG, handlers=[handler, file_handler])

#     # When data comes in, append to the 'data' array.
#     async def on_datasource_interval(
#         self, strategy, topic: str, data_list: List[Dict[str, str]]
#     ):
#         logging.info(f"Received data_list: {data_list}")
#         if topic not in self.data_map or not self.data_map[topic]:
#             logging.error(f"No data found for topic: {topic}")
#             return
#         datasource_data = self.data_map[topic]
#         self.data.append(datasource_data[-1])

#     async def on_backtest_complete(self, strategy):
#         df = pd.DataFrame(self.data)
#         if df.empty:
#             logging.warning("No data collection, skipping CSV export.")
#             return
#         df["start_time"] = df["start_time"].astype(float)
#         df = df[df["start_time"] >= START_TIME.timestamp()*1000]
#         df = df.drop_duplicates(subset=["start_time"])
#         df["time"] = pd.to_datetime(df["start_time"], unit="ms")
#         df.to_csv(FILE_NAME, encoding="utf-8", index=False)


# config = RuntimeConfig(
#     mode=RuntimeMode.Backtest,
#     datasource_topics=[
#         DATASOURCE_TOPIC
#     ],
#     candle_topics=[
#         # CANDLE_TOPIC
#     ],
#     active_order_interval=1,
#     start_time=START_TIME,
#     end_time=END_TIME,
#     data_count=100,
#     api_key=API_KEY,
#     api_secret=API_SECRET
# )


# permutation = Permutation(config)
# hyper_parameters = {}

# async def test_datamap():
#     await permutation.run(hyper_parameters, Strategy)

# asyncio.run(test_datamap())



import time
import pytz
import requests
import pandas as pd
from datetime import datetime

endpoints = [
    "coinglass|1m|futures/globalLongShortAccountRatio/history?exchange=Binance&symbol=BTCUSDT&interval=1d",
    # "cryptoquant|btc/market-data/funding-rates?window=hour&exchange=binance"
]

API_URL = "https://api.datasource.cybotrade.rs"

start_time = int(
    datetime(year=2020, month=1, day=1, tzinfo=timezone.utc).timestamp() * 1000
)
end_time = int(
    datetime(year=2024, month=1, day=1, tzinfo=timezone.utc).timestamp() * 1000
)
current_quota = 0
reset_time = 0
all_quota = 10000
for topic in endpoints:
    try:
        print(
            f"all_quota: {all_quota}, current_quota : {current_quota}, reset_time: {reset_time}"
        )
        if all_quota - current_quota <= 0:
            time.sleep(reset_time / 1000)
            print(f"Sleep for {reset_time}")
        provider = topic.split("|")[0]
        endpoint = topic.split("|")[-1]
        url = f"{API_URL}/{provider}/{endpoint}&start_time={start_time}&endTime={end_time}&limit=50000"
        print(f"--------------------------------")
        print(f"{url}")
        response = requests.get(
            url,
            headers={"X-API-KEY": API_KEY},
        )
        print(response.reason)
        print(response.status_code)
        print(response.text)
        all_quota = int(response.headers["X-Api-Limit"])
        current_quota = int(response.headers["X-Api-Limit-Remaining"])
        reset_time = int(response.headers["X-Api-Limit-Reset-Timestamp"])
        print(
            f"all_quota: {all_quota}, current_quota : {current_quota}, reset_time: {reset_time}"
        )
        
        data = response.json()["data"]
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["start_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert("Asia/Taipei")
        print(f"Done fetch {topic}")
        print(df)
        df.to_csv("long_short_BTC_1h.csv", encoding="utf-8-sig", index=False)
    except Exception as e:
        print(response.status_code)
        print(f"Failed to fetch {topic} : {e}")