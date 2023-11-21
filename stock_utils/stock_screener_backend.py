import traceback
import random
import pandas_ta as ta
from mauka_api.stock_utils.utils.date_util import (
    get_today_date,
    get_n_past_date,
    DEFAULT_FORMAT,
)
from mauka_api.stock_utils.utils.yfinance_util import download_multiples
from mauka_api.stock_utils.signal import Signal
from mauka_api.stock_utils.utils.technicals_utils import get_macd, get_rsi_timeseries
from mauka_api.stock_utils import get_last_trend
import threading
import time


def prepare_ema_smas(df):
    df["EMA5"] = ta.ema(df.Close, length=5)
    df["EMA3"] = ta.ema(df.Close, length=3)
    df["EMA20"] = ta.ema(df.Close, length=20)
    df["SMA20"] = ta.sma(df.Close, length=20)


def run_main(df, ticker, interval, trends):
    prepare_ema_smas(df)
    get_rsi_timeseries(df, 3)
    get_rsi_timeseries(df, 12)
    get_macd(df, "Close", 26, 12, 9)
    signal = Signal(ticker, interval, trends)
    random_scnd_to_sleep = random.uniform(0.200, 2)
    time.sleep(random_scnd_to_sleep)
    price_msg = signal.price_action(df)
    random_scnd_to_sleep = random.uniform(0.200, 2)
    time.sleep(random_scnd_to_sleep)
    rsi_msg = signal.rsi(df)


### Start Here
def fetch_data(tickers: list, start_date, end_date, interval="1d"):
    if not end_date:
        end_date = get_today_date(utc=False)
        if interval == "1d":
            last_n_days = -180
        elif interval == "1wk":
            last_n_days = -365
        elif interval == "1h":
            last_n_days = -10
        else:
            last_n_days = 200
    if not start_date:
        start_date = get_n_past_date(last_n_days, DEFAULT_FORMAT)
    last_known_trends = get_last_trend()
    tickersDf = download_multiples(tickers, start_date, end_date, interval)
    reordered_df = tickersDf.reorder_levels([1, 0], axis=1)
    for ticker in tickers:
        try:
            df = reordered_df[ticker]
            x = threading.Thread(
                target=run_main,
                args=(df, ticker, interval, last_known_trends),
            )
            print("Main : before running thread")
            x.start()
            print("Main : all done")
        except Exception as e:
            print(f"Failed to fetch Data : {e} :  {traceback.format_exc()}")
