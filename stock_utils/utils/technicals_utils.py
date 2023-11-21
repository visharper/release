import pandas_ta as ta
import pandas as pd


def get_rsi_timeseries(df, n=12):
    # First, calculate the gain or loss from one price to the next. The first value is nan so replace with 0.
    prices = df.Close
    deltas = (prices - prices.shift(1)).fillna(0)

    # Calculate the straight average seed values.
    # The first delta is always zero, so we will use a slice of the first n deltas starting at 1,
    # and filter only deltas > 0 to get gains and deltas < 0 to get losses
    avg_of_gains = deltas[1 : n + 1][deltas > 0].sum() / n
    avg_of_losses = -deltas[1 : n + 1][deltas < 0].sum() / n

    # Set up pd.Series container for RSI values
    rsi_series = pd.Series(0.0, deltas.index)
    # Now calculate RSI using the Wilder smoothing method, starting with n+1 delta.
    up = lambda x: x if x > 0 else 0
    down = lambda x: -x if x < 0 else 0
    i = n + 1
    for d in deltas[n + 1 :]:
        avg_of_gains = ((avg_of_gains * (n - 1)) + up(d)) / n
        avg_of_losses = ((avg_of_losses * (n - 1)) + down(d)) / n
        if avg_of_losses != 0:
            rs = avg_of_gains / avg_of_losses
            rsi_series[i] = 100 - (100 / (1 + rs))
        else:
            rsi_series[i] = 100
        i += 1
    df[f"RSI{n}"] = rsi_series


def get_rsi_timeseries_depricated(ticker, df, n=12):
    # First, calculate the gain or loss from one price to the next. The first value is nan so replace with 0.
    prices = df.Close[ticker]
    deltas = (prices - prices.shift(1)).fillna(0)

    # Calculate the straight average seed values.
    # The first delta is always zero, so we will use a slice of the first n deltas starting at 1,
    # and filter only deltas > 0 to get gains and deltas < 0 to get losses
    avg_of_gains = deltas[1 : n + 1][deltas > 0].sum() / n
    avg_of_losses = -deltas[1 : n + 1][deltas < 0].sum() / n

    # Set up pd.Series container for RSI values
    rsi_series = pd.Series(0.0, deltas.index)
    # Now calculate RSI using the Wilder smoothing method, starting with n+1 delta.
    up = lambda x: x if x > 0 else 0
    down = lambda x: -x if x < 0 else 0
    i = n + 1
    for d in deltas[n + 1 :]:
        avg_of_gains = ((avg_of_gains * (n - 1)) + up(d)) / n
        avg_of_losses = ((avg_of_losses * (n - 1)) + down(d)) / n
        if avg_of_losses != 0:
            rs = avg_of_gains / avg_of_losses
            rsi_series[i] = 100 - (100 / (1 + rs))
        else:
            rsi_series[i] = 100
        i += 1
    df[f"RSI{n}"] = rsi_series


def prepare_rsi(df, range):
    change = df["Close"].diff()
    change.dropna(inplace=True)
    # Create two copies of the Closing price Series
    change_up = change.copy()
    change_down = change.copy()

    #
    change_up[change_up < 0] = 0
    change_down[change_down > 0] = 0

    # Verify that we did not make any mistakes
    change.equals(change_up + change_down)

    # Calculate the rolling average of average up and average down
    avg_up = change_up.rolling(range).mean()
    avg_down = change_down.rolling(range).mean().abs()
    rsi = 100 * avg_up / (avg_up + avg_down)
    # Take a look at the 20 oldest datapoints
    #     rsi.head(12)
    df[f"RSI{range}"] = rsi


def perpare_emas(df, length_list=[], field="Close"):
    for days in length_list:
        df[f"EMA{days}"] = ta.ema(df[field], length=days)


def prepare_smas(df, length_list=[]):
    for days in length_list:
        df[f"SMA{days}"] = ta.sma(df.Close, length=days)


def previous_day_data(df, field):
    df[f"PREVIOUS_{field}"] = df[field].shift(1)


def previous_day_data_growth(df, field):
    df[f"{field}_GROW"] = df[field] > df[f"PREVIOUS_{field}"].shift(1)


def load_df_with_buy_sell_price(df, ticker):
    TotSignal = [0] * len(df)
    BuySellSignal = [0] * len(df)
    BuySellValue = [0] * len(df)
    global_buy = 0
    BuyPrice = [0] * len(df)
    SellPrice = [0] * len(df)
    buyPrice = 0
    sellPrice = 0
    for row in range(0, len(df)):
        TotSignal[row] = 0
        BuySellSignal[row] = 0
        if df.EMAsignal[row] == 1:
            TotSignal[row] = 1
            if global_buy != 1:
                global_buy = 1
                BuySellSignal[row - 1] = global_buy
                BuySellValue[row] = df.EMA3[row]
                buyPrice = df.Open[row]
            else:
                BuySellSignal[row] = 0
        elif df.EMAsignal[row] == 2:
            TotSignal[row] = 2
            if global_buy != 2 and global_buy == 1:
                global_buy = 2
                BuySellSignal[row] = global_buy
                BuySellValue[row] = df.High[row]
                sellPrice = df.High[row]
            else:
                BuySellSignal[row] = 0
        BuyPrice[row] = buyPrice
        SellPrice[row] = sellPrice

        df["BuySell"] = BuySellSignal
        df["BuySellValue"] = BuySellValue
        df["TotSignal"] = TotSignal
        df["BuyPrice"] = BuyPrice
        df["SellPrice"] = SellPrice


def load_df_with_buy_sell_columns(df, ticker):
    TotSignal = [0] * len(df)
    BuySellSignal = [0] * len(df)
    BuySellValue = [0] * len(df)
    global_buy = 0
    buy_price = 0
    TickerValue = [0] * len(df)
    for row in range(0, len(df)):
        TotSignal[row] = 0
        BuySellSignal[row] = buy_price
        TickerValue[row] = ticker
        if df.EMAsignal[row] == 1:
            TotSignal[row] = 1
            if global_buy != 1:
                global_buy = 1
                BuySellSignal[row] = global_buy
                BuySellValue[row] = df.Close[row]
                buy_price = df.Close[row]
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


def get_macd_data(df, tag, slow, fast, smooth):
    """_summary_
    Usage:
    googl_macd = get_macd(googl['close'], 26, 12, 9)
    Args:
        df (_type_): Dataframe to add macd signals in
        price (_type_): _description_
        slow (_type_): _description_
        fast (_type_): _description_
        smooth (_type_): _description_

    Returns:
        _type_: _description_
    """
    price = df[tag]
    exp1 = price.ewm(span=fast, adjust=False).mean()
    exp2 = price.ewm(span=slow, adjust=False).mean()
    df["macd"] = pd.DataFrame(exp1 - exp2)
    macd = df["macd"]
    df["signal"] = macd.ewm(span=smooth, adjust=False).mean()
    df["hist"] = df["macd"] - df["signal"]
    # frames =  [macd, signal, hist]


def get_macd(df, tag, slow, fast, smooth):
    """_summary_
    Usage:
    googl_macd = get_macd(googl['close'], 26, 12, 9)
    Args:
        df (_type_): Dataframe to add macd signals in
        price (_type_): _description_
        slow (_type_): _description_
        fast (_type_): _description_
        smooth (_type_): _description_

    Returns:
        _type_: _description_
    """
    price = df[tag]
    exp1 = price.ewm(span=fast, adjust=False).mean()
    exp2 = price.ewm(span=slow, adjust=False).mean()
    # df["macd"] = pd.DataFrame(exp1 - exp2)
    df.loc[:, "macd"] = pd.DataFrame(exp1 - exp2)
    macd = df["macd"]
    # df["signal"] = macd.ewm(span=smooth, adjust=False).mean()
    df.loc[:, "signal"] = macd.ewm(span=smooth, adjust=False).mean()
    # df["hist"] = df["macd"] - df["signal"]
    df.loc[:, "hist"] = df["macd"] - df["signal"]


def get_macd_deprecated(ticker, df, tag, slow, fast, smooth):
    """_summary_
    Usage:
    googl_macd = get_macd(googl['close'], 26, 12, 9)
    Args:
        df (_type_): Dataframe to add macd signals in
        price (_type_): _description_
        slow (_type_): _description_
        fast (_type_): _description_
        smooth (_type_): _description_

    Returns:
        _type_: _description_
    """
    price = df[tag][ticker]
    exp1 = price.ewm(span=fast, adjust=False).mean()
    exp2 = price.ewm(span=slow, adjust=False).mean()
    df["macd"] = pd.DataFrame(exp1 - exp2)
    macd = df["macd"]
    df["signal"] = macd.ewm(span=smooth, adjust=False).mean()
    df["hist"] = df["macd"] - df["signal"]


def get_macd_bakup(df, price, slow, fast, smooth):
    """_summary_
    Usage:
    googl_macd = get_macd(googl['close'], 26, 12, 9)
    Args:
        df (_type_): Dataframe to add macd signals in
        price (_type_): _description_
        slow (_type_): _description_
        fast (_type_): _description_
        smooth (_type_): _description_

    Returns:
        _type_: _description_
    """
    exp1 = price.ewm(span=fast, adjust=False).mean()
    exp2 = price.ewm(span=slow, adjust=False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns={"close": "macd"})
    signal = pd.DataFrame(macd.ewm(span=smooth, adjust=False).mean()).rename(
        columns={"macd": "signal"}
    )
    hist = pd.DataFrame(macd["macd"] - signal["signal"]).rename(columns={0: "hist"})
    # frames =  [macd, signal, hist]
    df["macd"] = macd
    df["signal"] = signal
    df["hist"] = hist
    # df = pd.concat(frames, join = 'inner', axis = 1)
    # return df


# def plot_macd(prices, macd, signal, hist):
#     ax1 = plt.subplot2grid((8,1), (0,0), rowspan = 5, colspan = 1)
#     ax2 = plt.subplot2grid((8,1), (5,0), rowspan = 3, colspan = 1)

#     ax1.plot(prices)
#     ax2.plot(macd, color = 'grey', linewidth = 1.5, label = 'MACD')
#     ax2.plot(signal, color = 'skyblue', linewidth = 1.5, label = 'SIGNAL')

#     for i in range(len(prices)):
#         if str(hist[i])[0] == '-':
#             ax2.bar(prices.index[i], hist[i], color = '#ef5350')
#         else:
#             ax2.bar(prices.index[i], hist[i], color = '#26a69a')

#     plt.legend(loc = 'lower right')

# plot_macd(googl['close'], googl_macd['macd'], googl_macd['signal'], googl_macd['hist'])
