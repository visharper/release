import traceback
import pandas_ta as ta
from mauka_api.stock_utils.utils.date_util import (
    get_today_date,
    get_n_past_date,
    DEFAULT_FORMAT,
)
from mauka_api.stock_utils.utils.yfinance_util import download_data
from mauka_api.stock_utils.signal import Signal
from mauka_api.stock_utils.utils.technicals_utils import get_macd, get_rsi_timeseries


def prepare_ema_smas(df):
    df["EMA5"] = ta.ema(df.Close, length=5)
    df["EMA3"] = ta.ema(df.Close, length=3)
    df["EMA20"] = ta.ema(df.Close, length=20)
    df["SMA20"] = ta.sma(df.Close, length=20)


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
            prepare_ema_smas(df)
            get_rsi_timeseries(df, 3)
            get_rsi_timeseries(df, 12)
            get_macd(df, "Close", 26, 12, 9)
            signal = Signal(ticker, interval)
            price_msg = signal.price_action(df)
            # print(ticker, " Price Msg : ", price_msg)
            # if price_msg.get(SIGNAL_MESSAGE_TYPE, ""):
            #     store_message(price_msg)
            rsi_msg = signal.rsi(df)
            # print(ticker, " RSI Msg : ", rsi_msg)
            # if rsi_msg.get(SIGNAL_MESSAGE_TYPE, ""):
            #     store_message(rsi_msg)

        except Exception as e:
            print(f"Failed to fetch Data : {e} :  {traceback.format_exc()}")
