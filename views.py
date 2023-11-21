from rest_framework.views import APIView
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework import status
from mauka_api.stock_utils import store_message
from .models import User, Signal, Trend
from .serializers import UserSerializer, SignalSerializer, TrendSerializer
from rest_framework.pagination import LimitOffsetPagination
from .stock_utils.stock_screener_ui import fetch_data_to_backtest

from mauka_api.utils.date_util import get_today_date, CREATE_DATE_FORMAT

RANGE = "range"
TICKER = "ticker"
TICKERS = "tickers"
INTERVAL = "interval"


from django.db import connections, connection
from django.db import transaction


def run_atomic(sql):
    with transaction.atomic():  # Here
        with connection.cursor() as cursor:
            cursor.execute(sql)
            for row in cursor.fetchall():
                return row


def execute_sql(sql):
    cursor = connections["default"].cursor()
    cursor.execute(sql)
    resp = cursor.fetchall()
    # print()
    # manually close the cursor if you are done!
    cursor.close()
    return resp


class SignalListApiView(APIView):
    def get(self, request):
        response = store_message({})
        if response:
            return Response(response, status=status.HTTP_200_OK)
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class MaukaListApiView(APIView):
    # add permission to check if user is authenticated
    # permission_classes = [permissions.IsAuthenticated]

    # 1. List all
    # def get(self, request, *args, **kwargs):
    #     '''
    #     List all the Mauka items for given requested user
    #     '''

    #     # Maukas = Mauka.objects.filter(ticker = request.ticker)
    #     print(request.data)
    #     Maukas = Mauka.objects.all()
    #     serializer = MaukaSerializer(Maukas, many=True)
    #     return Response(None, status=status.HTTP_200_OK)

    # 2. Create
    # {"ticker":"NVDA", "range": "weekly"}
    def post(self, request, *args, **kwargs):
        """
        Create the Mauka with given Mauka data
        """

        data = {TICKERS: request.data.get(TICKERS), RANGE: request.data.get(RANGE)}
        print("--------------------------")
        print(request.data)
        print("--------------------------")
        # response = request.data
        response = fetch_data_to_backtest(data.get(TICKERS, []))
        if response:
            return Response(response, status=status.HTTP_200_OK)

        # serializer = MaukaSerializer(data=data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(response, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def userApi(request, id=0):
    if request.method == "GET":
        users = User.objects.all()
        user_serializer = UserSerializer(users, many=True)
        return JsonResponse(user_serializer.data, safe=False)
    elif request.method == "POST":
        user_req = JSONParser().parse(request)
        user_serializer = UserSerializer(data=user_req)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse("Added Successfully", safe=False)
        return JsonResponse("Failed To Add", safe=False)


@csrf_exempt
def userDetail(request, username="vishal", format=None):
    if request.method == "GET":
        users = User.objects.get(username)
        user_serializer = UserSerializer(users, many=True)
        return JsonResponse(user_serializer.data, safe=False)
    elif request.method == "POST":
        user_req = JSONParser().parse(request)
        user_serializer = UserSerializer(data=user_req)
        if user_serializer.is_valid():
            user_serializer.save()
            return JsonResponse("Added Successfully", safe=False)
        return JsonResponse("Failed To Add", safe=False)


@csrf_exempt
def trendAPI(request, format=None):
    print("----- TREND _API -------")
    if request.method == "GET":
        try:
            query = """
                 select ms1.ticker, ms1.time_range, ms1.category, message
                from mauka_api_signal ms1, 
                    (select ticker, category, time_range, max(create_date) LastUpdate 
                    from mauka_api_signal group by ticker, category, time_range) ms2
                where ms1.ticker = ms2.ticker
                and ms1.create_date = LastUpdate
                order by ms1.ticker;
            """
            response = execute_sql(query)
            if response:
                return JsonResponse(response, safe=False)
            return JsonResponse("Failed To retreive trend", safe=False)
        except Exception as e:
            print("Exception occurred during trendAPI : ", e)
    # if request.method == "GET":
    #     try:
    #         query = """
    #              select ms1.ticker, time_range, category, message
    #             from mauka_api_signal ms1,
    #                 (select ticker, max(create_date) LastUpdate
    #                 from mauka_api_signal group by ticker) ms2
    #             where ms1.ticker = ms2.ticker
    #             and ms1.create_date = LastUpdate
    #             order by ms1.ticker
    #         """
    #         response = execute_sql(query)
    #         if response:
    #             return JsonResponse(response, safe=False)
    #         return JsonResponse("Failed To retreive trend", safe=False)
    #     except Exception as e:
    #         print("Exception occurred during trendAPI : ", e)


@csrf_exempt
def signalDetail(request, range=[], format=None):
    if request.method == "GET":
        try:
            today_date = get_today_date(CREATE_DATE_FORMAT, utc=True)
            if not range:
                range = ["2023-10-01", today_date]
            signals = Signal.objects.filter(create_date__range=range).order_by(
                "-create_date"
            )
            signal_serializer = SignalSerializer(signals, many=True)
            if signal_serializer:
                return JsonResponse(signal_serializer.data[:100], safe=False)
            return Response(f"Failed to fetch : ", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception occurred during signal detail: ", e)

    elif request.method == "POST":
        req = JSONParser().parse(request)
        serializer = SignalSerializer(data=req)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse("Added Successfully", safe=False)
        return JsonResponse(f"Failed To Add due to : {serializer}", safe=False)


@csrf_exempt
def backtestApi(request, format=None):
    if request.method == "POST":
        req = JSONParser().parse(request)
        print("Request :  ", req)
        tickers = req.get("tickers")
        interval = req.get("interval")
        start_date = req.get("start_date", "")
        end_date = req.get("end_date", "")
        response = fetch_data_to_backtest(
            tickers=tickers, interval=interval, start_date=start_date, end_date=end_date
        )
        if response:
            return JsonResponse(response, safe=False)
        return JsonResponse(f"Failed To Pull Data", safe=False)


@csrf_exempt
def watchListApi(request, format=None):
    if request.method == "GET":
        try:
            trends = Trend.objects.all()  # (ticker__in=tickers).order_by("ticker")
            trend_serializer = TrendSerializer(trends, many=True)
            if trend_serializer:
                return JsonResponse(trend_serializer.data, safe=False)
            # return Response(f"Failed to fetch : ", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception occurred during signal detail: ", e)
    elif request.method == "POST":
        try:
            req = JSONParser().parse(request)
            print("Request :  ", req)
            tickers = req.get("tickers")
            trends = Trend.objects.filter(ticker__in=tickers).order_by("ticker")
            trend_serializer = TrendSerializer(trends, many=True)
            if trend_serializer:
                return JsonResponse(trend_serializer.data, safe=False)
            return Response(f"Failed to fetch : ", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Exception occurred during signal detail: ", e)


class backtestDetail(APIView):
    # {"ticker":"NVDA", "range": "weekly"}
    def post(self, request, *args, **kwargs):
        data = {
            TICKERS: request.data.get(TICKERS),
            INTERVAL: request.data.get(INTERVAL),
        }
        print("--------------------------")
        print(request.data)
        print("--------------------------")
        response = fetch_data_to_backtest(data.get(TICKERS, []))
        if response:
            return Response(response, status=status.HTTP_200_OK)
        # else:
        #     return Response(response.data, status=status.HTTP_201_CREATED)

        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class setTrends(APIView):
    # {"ticker":"NVDA", "range": "weekly"}
    def post(self, request, *args, **kwargs):
        ticker = request.data.get("ticker")
        trend = request.data.get("trend")
        period = request.data.get("period")
        update_dt = get_today_date(CREATE_DATE_FORMAT)
        """
        {"ticker":"CSCO", "trend":"Bullish", "period":"weekly", "update_dt":""}
        """
        update_qry = f"update mauka_api_trend set {period}='{trend}', {period}_update_dt = '{update_dt}' where ticker = '{ticker}' and weekly is not '{trend}';"
        response = Trend.objects.raw(update_qry)
        # print(response)
        if response:
            return Response("Success", status=status.HTTP_200_OK)
        # # else:
        # #     return Response(response.data, status=status.HTTP_201_CREATED)

        # return Response(response, status=status.HTTP_400_BAD_REQUEST)


# @csrf_exempt
# def trendsApi(request, format=None):
#     interval_map = {"1d": "daily", "1wk": "weekly", "1h": "hourly"}
#     if request.method == "POST":
#         req = JSONParser().parse(request)
#         print(f"Request Received: {req}")
#         ticker = req.get("ticker")
#         trend = req.get("trend")
#         interval = req.get("interval")
#         update_dt = get_today_date(CREATE_DATE_FORMAT, True)
#         print(f"Request Received: {req}")
#         period = interval_map[interval]

#         """
#         {"ticker":"CSCO", "trend":"Bullish", "period":"weekly", "update_dt":""}
#         """
#         update_qry = f"""
#         update mauka_api_trend set {period}='{trend}',
#         {period}_update_dt = '{update_dt}'
#         where ticker = '{ticker}' and {period} is not '{trend}';
#         """
#         response = Trend.objects.raw(update_qry)
#         if response:
#             return JsonResponse(response, safe=False)
#         return JsonResponse(f"Failed To Pull Data", safe=False)
