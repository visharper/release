import numpy as np
import json
from mauka_api.stock_utils import store_message, update_trend, MAUKA_EMAIL
from mauka_api.stock_utils.utils.send_csv_in_email import send_mail
from mauka_api.enums import CategoryEnum
from mauka_api import (
    # Signal DB Enums
    SIGNAL_CATEGORY,
    SIGNAL_MESSAGE,
    SIGNAL_MESSAGE_TYPE,
    SIGNAL_TICKER,
    SIGNAL_TIME_RANGE,
    NEUTRAL_VALUE,
    BULLISH_VALUE,
    BEARISH_VALUE,
)

# Category Enums
RSI = CategoryEnum.RSI.value
PRICE_ACTION = CategoryEnum.PRICE_ACTION.value


def bullish_buy(df):
    return np.where(
        (
            (
                (df["Low"] <= df["EMA3"]) & (df["EMA3"] <= df["High"])
            )  # Buy price should be in range of the day
            & (df["EMA3"] >= df["SMA20"])
            & (df["EMA20"] >= df["SMA20"])
            & (df["RSI3"] < 90)
            & (df["macd"] >= df["signal"])  # RSI is in Overbought Region
            & (df["hist"] > df["hist"].shift(1))  # Avoid buying if MACD is falling
            & (df["RSI3"] >= df["RSI12"])  # Avoid buying if HISTAGRAM is falling
            & (df["EMA3"] >= df["Open"])  # Avoid buying if RSI3 is below 12
            & (  # Avoid buying if there is a gap
                df["RSI3"] > df["RSI3"].shift(1)
            )  # Avoid buying if RSI is same or lower than previous
        ),
        BULLISH_VALUE,
        None,
    )
    # return np.where(
    #         (
    #             (df["EMA3"]>=df["SMA20"]) &
    #             (df["Close"]>=df["SMA20"]) &
    #             (df["Low"]<=df["EMA3"])  & # Avoid buying at price gap tentive to go down
    #             (df['macd'] >= df["signal"]) &
    #             (
    #                 (df['macd'] >= df["macd"].shift(1)) |
    #                 (df['signal'] >= df["signal"].shift(1))
    #             )
    #         ),
    #         "Buy",
    #         None
    # )


def bullish_sell(df, ema3, previous_ema3, OPEN, RSI, sma20, ema20):
    return np.where(((df["Low"] > df["EMA3"]) | (df[ema3] <= df[sma20])), "Sell", None)


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


def macd_filter(df):
    return np.where(
        ((df["MACD_BUY"] == "Bullish") & (df["MACD_TREND"] == "Bullish")), "Buy", None
    )


def rsi_filter(df):
    return np.where((df["RSI3"] >= 90), f"{BEARISH_VALUE}+90", None)


def prepare_email_body(ticker_data: dict):
    ticker = ticker_data.get(SIGNAL_TICKER)
    msg = ticker_data.get(SIGNAL_MESSAGE)
    msg_type = ticker_data.get(SIGNAL_MESSAGE_TYPE)
    category = ticker_data.get(SIGNAL_CATEGORY)
    interval = ticker_data.get(SIGNAL_TIME_RANGE)
    return (
        f"{msg_type} trend identified for "
        f"{ticker} for interval {interval} "
        f"based on {category}"
    )


def get_last_known_trend_for_ticker(
    trends: list, ticker: str, interval: str, category: str
):
    """trends is list is lists with ticker trend
    list contain [ticker, interval, last_Trend]

    Args:
        trends (list): _description_
        ticker (str): _description_
        interval (str): _description_
    """
    for trend in trends:
        if trend[0] == ticker and trend[1] == interval and trend[2] == category:
            return trend[3]
    return False


class Signal:
    def __init__(self, ticker, interval, trends):
        self.resp = dict()
        self.resp[SIGNAL_TIME_RANGE] = interval
        self.resp[SIGNAL_TICKER] = ticker
        self.ticker = ticker
        self.trends = trends

    def price_action(self, df):
        try:
            price_resp = self.resp
            price_resp[SIGNAL_CATEGORY] = "price"
            price_resp[SIGNAL_MESSAGE] = NEUTRAL_VALUE
            price_resp[SIGNAL_MESSAGE_TYPE] = NEUTRAL_VALUE
            message = bullish_buy(df)
            new_trend = message[len(message) - 1]
            last_trend = get_last_known_trend_for_ticker(
                self.trends,
                self.ticker,
                self.resp[SIGNAL_TIME_RANGE],
                price_resp[SIGNAL_CATEGORY],
            )
            if new_trend:
                price_resp[SIGNAL_MESSAGE] = new_trend
                price_resp[SIGNAL_MESSAGE_TYPE] = BULLISH_VALUE
                # update_trend(price_resp)
                # email_subject = prepare_email_body(price_resp)
                # send_mail("Mauka Price Action Alert", MAUKA_EMAIL, email_subject)
            print(
                self.ticker,
                " PRICE ===> ",
                price_resp[SIGNAL_MESSAGE],
                " == ",
                last_trend,
            )
            if not price_resp[SIGNAL_MESSAGE] == last_trend:
                store_message(price_resp)
            return price_resp
        except Exception as e:
            print(f"!! Exception  Found: {e}")
            pass

    def rsi(self, df):
        rsi_resp = self.resp
        rsi_resp[SIGNAL_CATEGORY] = RSI
        rsi_resp[SIGNAL_MESSAGE] = NEUTRAL_VALUE
        rsi_resp[SIGNAL_MESSAGE_TYPE] = NEUTRAL_VALUE
        message = rsi_filter(df)
        new_trend = message[len(message) - 1]
        last_trend = get_last_known_trend_for_ticker(
            self.trends,
            self.ticker,
            self.resp[SIGNAL_TIME_RANGE],
            rsi_resp[SIGNAL_CATEGORY],
        )
        if new_trend:  # If there is any signal
            rsi_resp[SIGNAL_MESSAGE] = new_trend
            rsi_resp[SIGNAL_MESSAGE_TYPE] = BEARISH_VALUE

        print(self.ticker, " RSI ===> ", rsi_resp[SIGNAL_MESSAGE], " == ", last_trend)
        if not rsi_resp[SIGNAL_MESSAGE] == last_trend:
            store_message(rsi_resp)
            # update_trend(rsi_resp)
            # email_subject = prepare_email_body(rsi_resp)
            # send_mail("Mauka RSI  Alert", MAUKA_EMAIL, email_subject)
        return rsi_resp
