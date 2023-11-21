import sys
import traceback
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter
import pandas as pd
import pandas_ta as ta
import numpy as np
from datetime import date, timedelta
import ssl
from mauka_api.stock_utils.utils.date_util import (
    get_today_date,
    get_n_past_date,
    DEFAULT_FORMAT,
)
from mauka_api.stock_utils.utils.yfinance_util import download_data
from mauka_api.stock_utils.signal import Signal
from mauka_api.stock_utils.utils.technicals_utils import get_macd, get_rsi_timeseries


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


session = CachedLimiterSession(
    limiter=Limiter(
        RequestRate(2, Duration.SECOND * 5)
    ),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)
session.headers["User-agent"] = "my-program/1.0"
# SSL Required for Requests webscrapping
ssl._create_default_https_context = ssl._create_unverified_context


def bullish_buy(df, sma20, ema20, ema3, ema5):
    return (df[ema5] >= df[ema20]) & (df[ema3] > df[ema5])


def bullish_sell(df, sma20, ema20, ema3, ema5, close, open):
    diff = df[ema3] - df[ema5]
    percent = diff / df[ema3]
    is_price_rising = percent <= 0.004
    is_bullish = df[ema20] >= df[sma20]
    is_close_eq_ema3 = df[close] <= df[ema3]
    is_closed_lower = df[close] < df[open]
    return is_closed_lower


def prepare_ema_smas(df):
    df["EMA5"] = ta.ema(df.Close, length=5)
    df["EMA3"] = ta.ema(df.Close, length=3)
    df["EMA20"] = ta.ema(df.Close, length=20)
    df["SMA20"] = ta.sma(df.Close, length=20)


def prepare_buy_sell_conditions(df):
    conditions = [
        (bullish_buy(df, "SMA20", "EMA20", "EMA3", "EMA5")),
        (bullish_sell(df, "SMA20", "EMA20", "EMA3", "EMA5", "Close", "Open")),
    ]
    choices = [1, 2]
    df["EMAsignal"] = np.select(conditions, choices, default=0)


def load_df_with_buy_sell_columns(df, ticker):
    TotSignal = [0] * len(df)
    BuySellSignal = [0] * len(df)
    BuySellValue = [0] * len(df)
    global_buy = 0
    TickerValue = [0] * len(df)
    for row in range(0, len(df)):
        TotSignal[row] = 0
        BuySellSignal[row] = 0
        TickerValue[row] = ticker
        if df.EMAsignal[row] == 1:
            TotSignal[row] = 1
            if global_buy != 1:
                global_buy = 1
                BuySellSignal[row] = global_buy
                BuySellValue[row] = df.Close[row]

            else:
                BuySellSignal[row] = 0
        elif df.EMAsignal[row] == 2:
            TotSignal[row] = 2
            if global_buy != 2 and global_buy == 1:
                global_buy = 2
                BuySellSignal[row] = global_buy
                BuySellValue[row] = df.Close[row]
            else:
                BuySellSignal[row] = 0

    df["BuySell"] = BuySellSignal
    df["BuySellValue"] = BuySellValue
    df["TotSignal"] = TotSignal
    df["Ticker"] = TickerValue
    print(df)
    result = df.to_json(orient="split")
    return result


def prepare_output(df, ticker, report_name):
    today = date.today()
    d = timedelta(days=2)  # Fetch Buy signals for last 2 days
    a = str(today - d)
    filter = df["BuySell"] == 1
    date_filter = df["Date"] >= a
    # filtering data
    buy_df = df.where(filter & date_filter)
    buy_df.dropna(inplace=True)
    if not buy_df.empty:
        # print(f"------- {ticker} ----------")
        print(buy_df, type(buy_df))
        # buy_df.to_csv(report_name, mode="a", index=False, header=True)


### Start Herex
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
    for ticker in tickers:
        try:
            df = download_data(ticker, start_date, end_date, interval)
            print(df)
            prepare_ema_smas(df)
            get_rsi_timeseries(df, 3)
            get_rsi_timeseries(df, 12)
            get_macd(df, "Close", 26, 12, 9)
            signal = Signal(ticker, interval)
            price_msg = signal.price_action(df)
            rsi_msg = signal.rsi(df)

        except Exception as e:
            print(f"Failed to fetch Data : {e} :  {traceback.format_exc()}")
