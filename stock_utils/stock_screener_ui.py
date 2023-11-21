import json
import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
import requests_cache
import ssl
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter
import pandas as pd
import pandas_ta as ta
import numpy as np
from datetime import datetime, date, timedelta
from backtesting import Backtest
from .utils.technicals_utils import get_macd, get_rsi_timeseries
from .utils.yfinance_util import download_data
from .utils.date_util import get_today_date, get_n_past_date, DEFAULT_FORMAT
from .signal import Signal
from .utils.backtest import MyStrat


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


def perpare_rsi_signal(rsi3, rsi12):
    if rsi3 > 90:
        return 2
    elif rsi3 < 30:
        return 0
    elif rsi3 < rsi12:
        return 2
    else:
        return 1


def prepare_macd_signal(macd, signal):
    buySignal = 0

    if macd >= signal and macd <= 0:
        # handles if macd is increasing
        buySignal = 1

    if macd < signal:
        # handles if macd is decreasing
        buySignal = 2
    return buySignal


def load_df_with_buy_sell_columns(df, ticker):
    TotSignal = [0] * len(df)
    BuySellSignal = [0] * len(df)
    BuyValue = [0] * len(df)
    SellValue = [0] * len(df)
    RsiSignal = [0] * len(df)
    MacdSignal = [0] * len(df)
    global_buy = 0
    TickerValue = [0] * len(df)
    for row in range(0, len(df)):
        RsiSignal[row] = perpare_rsi_signal(df.RSI3[row], df.RSI12[row])
        MacdSignal[row] = prepare_macd_signal(df.macd[row], df.signal[row])
        TotSignal[row] = 0
        BuySellSignal[row] = 0
        TickerValue[row] = ticker
        if df.EMAsignal[row] == 1:
            TotSignal[row] = 1
            SellValue[row] = "null"
            BuyValue[row] = "null"
            if global_buy != 1:
                global_buy = 1
                BuySellSignal[row] = global_buy
                BuyValue[row] = df.EMA3[row]
            else:
                BuySellSignal[row] = 0
        elif df.EMAsignal[row] == 2:
            TotSignal[row] = 2
            SellValue[row] = "null"
            BuyValue[row] = "null"
            if global_buy != 2 and global_buy == 1:
                global_buy = 2
                BuySellSignal[row] = global_buy
                SellValue[row] = df.High[row]
            else:
                BuySellSignal[row] = 0
        else:
            BuyValue[row] = "null"
            SellValue[row] = "null"

    df["BuySell"] = BuySellSignal
    df["BuyValue"] = BuyValue
    df["SellValue"] = SellValue
    df["TotSignal"] = TotSignal
    df["Ticker"] = TickerValue
    df["RSI_SIGNAL"] = RsiSignal
    df["MACD_SIGNAL"] = MacdSignal
    # df.tail(10)
    # last_row = df.iloc[-5]
    # last_row.drop(labels=["Open","High","Low","Close","Adj Close","Volume","EMA5","EMA3","EMA20","SMA20","EMAsignal","RSI3","RSI12","macd","signal","hist","BuySell"])
    result = df.to_json(orient="records")
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
        buy_df.to_csv(report_name, mode="a", index=False, header=True)


### Start Here
def fetch_data_to_backtest(tickers: list, start_date="", end_date="", interval="1d"):
    resp = {}
    # today_date = get_today_date(utc=True)
    if not end_date:
        end_date = get_n_past_date(2, DEFAULT_FORMAT)
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
        signal = Signal(ticker, interval)
        if not ticker:
            continue
        df = download_data(ticker, start_date, end_date, interval)
        print(start_date, "----", end_date)
        # df.reset_index(inplace=True)  # Keep all the fields with headers in data frame
        if df.empty:
            return 0
        # df.Date = df.Date.apply(lambda d: datetime.strptime(str(d), "%Y-%m-%d"))
        prepare_ema_smas(df)
        prepare_buy_sell_conditions(df)
        get_rsi_timeseries(df, 3)
        get_rsi_timeseries(df, 12)
        get_macd(df, "Close", 26, 12, 9)
        df.tail(5)
        data = load_df_with_buy_sell_columns(df, ticker)
        signal.price_action(df)
        signal.rsi(df)
        resp["ticker_data"] = data
        # bt = Backtest(df, MyStrat, cash=10000)
        # stat = bt.run()
        # stat_str = str(stat)
        print(df.tail(5))
        resp["backtest_data"] = json.dumps("")
    return resp
