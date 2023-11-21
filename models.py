from django.db import models
from django.utils.timezone import now


class User(models.Model):
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, primary_key=True)
    phone = models.IntegerField(default=0)
    username = models.CharField(max_length=200)
    notification = models.CharField(max_length=1000)


class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tickers = models.CharField(max_length=5000)
    create_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)


class Recommendation(models.Model):
    tickers = models.CharField(max_length=10)
    hourly = models.CharField(max_length=20)
    daily = models.CharField(max_length=20)
    weekly = models.CharField(max_length=20)


class TickerData(models.Model):
    ticker = models.CharField(max_length=10, primary_key=True)


class Signal(models.Model):
    create_date = models.DateTimeField(auto_now_add=True, primary_key=True)
    ticker = models.CharField(max_length=10)  # TSLA,NVDA
    category = models.CharField(max_length=10)  # RSI, Price
    message = models.CharField(max_length=200)  # Raw Message
    message_type = models.CharField(max_length=15)  # Bullish/Bearish
    time_range = models.CharField(max_length=5)  # 1m, 1h, 1d, 360d


# class Notification(models.Model):
#     ticker = models.ForeignKey(max_length=10, on_delete=models.CASCADE) # TSLA,NVDA
#     user_email = models.ForeignKey(User, on_delete=models.CASCADE)
# class Mauka(models.Model):
#     ticker = models.CharField(max_length = 7)
#     timestamp = models.DateTimeField(auto_now_add = True, auto_now = False, blank = True)
#     range = models.CharField(max_length = 20,default = "daily")
# updated = models.DateTimeField(auto_now = True, blank = True)
# user = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True)

# def __str__(self):
#     return self.ticker


class Trend(models.Model):
    ticker = models.CharField(max_length=10, primary_key=True)
    weekly = models.CharField(max_length=200)
    weekly_update_dt = models.DateTimeField(auto_now_add=True)
    daily = models.CharField(max_length=200)
    daily_update_dt = models.DateTimeField(auto_now_add=True)


class SignalTrend(models.Model):
    create_date = models.DateTimeField(auto_now_add=True, primary_key=True)
    ticker = models.CharField(max_length=10)  # TSLA,NVDA
    category = models.CharField(max_length=10, blank=True)  # RSI, Price
    message = models.CharField(max_length=200, blank=True)  # Raw Message
    message_type = models.CharField(max_length=15)  # Bullish/Bearish
    time_range = models.CharField(max_length=5)  # 1m, 1h, 1d, 360d
