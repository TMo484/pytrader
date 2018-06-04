import pytrade_googledata as gd
import matplotlib.pyplot as plt
import numpy as np
import csv

period = 60         ## seconds per interval
lookback_days = 7  ## number of days to look back from today
target_return = 0.005

## standard x and y
x = 'index'
y = 'Open'


def pull_stock_data(ticker, period = period, days = lookback_days):
    df = gd.get_google_finance_intraday(ticker, period, days)
    df.reset_index(inplace=True)                                ## drop the date, move it to a column
    df.reset_index(inplace=True)                                ## move the numeric index to a column
    return df

def calc_trendline(df, x, y):
    z = np.polyfit(df[x], df[y], 1)
    p = np.poly1d(z)
    return z,p

def normalize_dataframe(df, x, y, p):
    norm_y = df[y]-p(df[x])
    stdev = norm_y.std()
    return stdev
    
def grade_stock(df, x=x, y=y):
    z, p = calc_trendline(df, x, y)
    stdev = normalize_dataframe(df, x, y, p)
    trend_direction = p[1]
    last_price = df[y].tail(n=1).values[0]
    expected_price = (p[0] + (p[1] * df.index.max())) * (1 + target_return)
    price_with_returns = last_price * (1 + target_return)
    lower_bound_price = (p[0] + p[1] * df.index.max()) - stdev
    price_slope = p[1]/p[0]
    volatility = stdev / p[0]
    average_volume = df['Volume'].sum() / lookback_days
    if price_with_returns < expected_price and price_with_returns > lower_bound_price and trend_direction > 0:
        rec_pos = 'Buy'
    else:
        rec_pos = 'Hold Off'
    return rec_pos, last_price, expected_price, price_with_returns, price_slope, volatility, average_volume 
    
    
## Below this line are functions used for visualization
def show_trended_dataframe(df, x=x, y=y):
    z, p = calc_trendline(df, x, y)
    stdev = normalize_dataframe(df, x, y, p)
    df.plot.line(x=x, y=y)
    plt.plot(df[x], p(df[x]), 'r--')
    plt.plot(df[x], p(df[x]) + stdev, 'g--')
    plt.plot(df[x], p(df[x]) - stdev, 'g--')
    plt.show()
    
def show_stock_analysis(ticker):
    df = pull_stock_data(ticker)
    show_trended_dataframe(df)
    rec_pos, last_price, expected_price, price_with_returns, price_slope, volatility, average_volume = grade_stock(df)
    print("Stock: {0}    Rating: {1}".format(ticker, rec_pos))
    print("Last Price: {0}    Price with Returns: {1}    Expected Price: {2}".format(last_price, price_with_returns, expected_price))
    
