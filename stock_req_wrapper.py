import pandas as pd
import numpy as np

from mauka_api.stock_utils.stock_screener_backend import fetch_data

sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
# sp500_list = np.array(sp500[0]['Symbol'])
S50_TICKERS_PD_ARRAY = np.array(sp500[0]["Symbol"])
S500_TICKERS_LIST = S50_TICKERS_PD_ARRAY.tolist()
# DEFAULT_TICKERS = [
#     "TSLA",
#     "NVDA",
#     "RIVN",
#     "XRX",
#     "XOM",
#     "BAC",
#     "SOFI",
#     "AI",
#     "INTC",
#     "GPS",
#     "CSCO",
#     "PLTR",
#     "VZ",
#     "VOD",
#     "GOLD",
# ]
# DEFAULT_TICKERS = ["CSL", "NVDA", "SOFI"]
# fetch_data(DEFAULT_TICKERS, start_date="2023-10-00 06:30:00", end_date="2023-10-16 12:30:00", interval="1h")
# fetch_data(DEFAULT_TICKERS, start_date="2023-10-00 06:30:00", end_date="2023-10-16 13:30:00", interval="1h")
# fetch_data(DEFAULT_TICKERS, start_date="", end_date="", interval="1h")
DEFAULT_TICKERS = ["SO", "SOFI"]
fetch_data(S500_TICKERS_LIST, start_date="", end_date="", interval="1d")
fetch_data(S500_TICKERS_LIST, start_date="", end_date="", interval="1wk")
