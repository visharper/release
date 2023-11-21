import yfinance as yf
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from pyrate_limiter import Duration, RequestRate, Limiter
import ssl
import pandas as pd
import numpy as np


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    pass


session = CachedLimiterSession(
    limiter=Limiter(
        RequestRate(2, Duration.SECOND * 5)
    ),  # max 2 requests per 5 seconds
    bucket_class=MemoryQueueBucket,
    backend=SQLiteCache("yfinance.cache"),
)
session.headers["User-agent"] = "yfinance-cache/1.0"
# SSL Required for Requests webscrapping
ssl._create_default_https_context = ssl._create_unverified_context


def download_data(ticker, start_date, end_date, interval="1d"):
    try:
        df = yf.download(ticker, start=start_date, end=end_date, interval=interval)
        # df = yf.download(tickers = ticker,  # list of tickers
        #         period = "30d",         # time period
        #         interval = interval,       # trading interval
        #         prepost = False,       # download pre/post market hours data?
        #         repair = True)         # repair obvious price errors e.g. 100x?ticker_history = yf.download(tickers = "tsla",  # list of tickers
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        print("######### EXCEPTION @############# : ", e)
        pass


def download_multiples(ticker_list: list, start_date, end_date, interval="1d"):
    return yf.download(
        tickers=ticker_list,
        start=start_date,
        end=end_date,
        interval=interval,
    )
