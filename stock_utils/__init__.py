import numpy as np
from mauka_api.enums.signal import SignalEnum
from mauka_api.stock_utils.utils.date_util import add_microseconds, DB_DATE_FORMAT

# importing the requests library
import requests
import json
import random
from mauka_api import (
    # Signal DB Enums
    SIGNAL_CREATE_DATE,
)

DATETIME = SignalEnum.DATETIME.value


# MAUKA_EMAIL = "2067506630@tmomail.net"
MAUKA_EMAIL = "maukatheopportunity@gmail.com"
# defining the api-endpoint
API_ENDPOINT = "http://localhost:8000/api/signal/"
TREND_API = "http://localhost:8000/api/trend/"

CATEGORIES = ["RSI", "PRICE"]


def get_last_trend():
    try:
        headers = {"Content-type": "application/json", "Accept": "application/json"}
        r = requests.get(url=TREND_API, headers=headers)
        print("Response ==> ", r.text, type(r))
        if r:
            return json.loads(r.text)
        return []

    except Exception as e:
        print("Exception Getting last Trend:", e)


def update_trend(msg: dict = {}):
    try:
        # setting trend for stock
        trend_req = {}
        headers = {"Content-type": "application/json", "Accept": "application/json"}
        print(f"----- ADDING update_trend : {msg}")
        #  {'time_range': '1d', 'ticker': 'WTW', 'category': 'rsi', 'message': 'Bearish+90', 'message_type': 'BEARISH'}
        trend_req["ticker"] = msg.get("ticker")
        trend_req["trend"] = msg.get("message_type")
        trend_req["interval"] = msg.get("time_range")
        r = requests.post(url=TREND_API, data=json.dumps(trend_req), headers=headers)
        # extracting response text
        print("Response ==> ", r)
        response = r.text
        print("Response ==> response ", response)
        if type(response) == str:
            return response
        return "Record Saved Succesfully"
    except Exception as e:
        print("Exception Storing Message to Found:", e)


def store_message(msg: dict = {}):
    try:
        # sending post request and saving response as response object
        headers = {"Content-type": "application/json", "Accept": "application/json"}
        random_int = random.randint(1, 1999)

        msg[SIGNAL_CREATE_DATE] = add_microseconds(random_int, DB_DATE_FORMAT, True)
        print(f"----- ADDING SIGNAL {msg}")
        r = requests.post(url=API_ENDPOINT, data=json.dumps(msg), headers=headers)
        # extracting response text
        response = r.text
        if type(response) == str:
            return response
        return "Record Saved Succesfully"
    except Exception as e:
        print("Exception Storing Message to Found:", e)


def bullish_buy(df):
    return np.where(
        ((df["EMA3"] >= df["SMA20"]) & (df["Close"] >= df["SMA20"])), "Buy", None
    )


def bullish_sell(df, ema3, previous_ema3, OPEN, RSI, sma20, ema20):
    return np.where((df[ema3] <= df[sma20]), "Sell", None)


def signal_all(df):
    conditions = [(bullish_buy(df)), (bullish_sell(df))]
    choices = [1, 2]
    df["EMAsignal"] = np.select(conditions, choices, default=0)


def price_action_filter(df):
    return np.where(
        (
            # (df['3-5'] < df['3-5'].shift(1)) &
            ((df.macd - df.signal) >= 0.5)
            & (df["RSI_BUY"] == "Bullish")
            & (df["MACD_BUY"] == "Bullish")
            & (df["RSI_TREND"] == "Bullish")
            & (df["MACD_TREND"] == "Bullish")
        ),
        "Buy",
        None,
    )


def rsi_filter(df):
    return np.where((df["RSI3"] >= 90), "Bearish+90", None)
