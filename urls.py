from django.urls import path, include

from .views import (
    MaukaListApiView,
    userApi,
    userDetail,
    signalDetail,
    SignalListApiView,
    backtestApi,
    watchListApi,
    trendAPI,
)

urlpatterns = [
    path("", MaukaListApiView.as_view()),
    path("user/", userApi),
    # path("user/(?P<username>.+)/$", userDetail),
    path("signal/", signalDetail),
    path("test/", SignalListApiView.as_view()),
    path("backtest/", backtestApi),
    path("watchlist/", watchListApi),
    path("trend/", trendAPI),
]
