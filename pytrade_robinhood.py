from Robinhood import Robinhood
import pandas as pd
import requests


securities_columns = ['Buy Price', 'Shares Held', 'Stock Instrument', 'Shares Pending Sale']

#Set up the trader
trader = Robinhood()

#Log the trader in
user = input("Please input username: ")
pw = input("Please login to account {0}: ".format(user))
trader.login(username=user, password=pw)


#Obtain the stock instrument from a ticker
def get_stock_instrument(ticker):
    return trader.instruments(ticker)[0]

def get_bid_price(instrument):
    return requests.get(instrument['quote']).json()['ask_price']

#Buy shares of stock from ticker
def buy_order(ticker, num_shares):
    instrument = get_stock_instrument(ticker)
    bid_price = float(get_bid_price(instrument))
#    trader.place_market_buy_order(instrument_URL=instrument, symbol=ticker, time_in_force='GTC', quantity=num_shares)
    trader.place_buy_order(instrument=instrument, quantity=num_shares, bid_price=bid_price)

def sell_order(ticker, instrument, num_shares, order_type, min_price, time_in_force='GTC'):
    if order_type == 'market':
        trader.place_sell_order(instrument, num_shares)
    elif order_type == 'limit':
        trader.place_limit_sell_order(instrument, ticker, time_in_force, min_price, num_shares)
    else:
        raise ValueError('Unexpected order_type (Function: sell_order)')

def find_owned_securities():
    owned_securities = []
    securities_details = []
    for i in trader.securities_owned()['results']:
        owned_securities.append(requests.get(i['instrument']).json()['symbol'])
        securities_details.append([i['average_buy_price'], i['quantity'], i['instrument'], i['shares_held_for_sells']])
    df_securities = pd.DataFrame(data=securities_details, columns=securities_columns, index=owned_securities)
    return df_securities

def find_available_cash():
    return float(trader.portfolios()['equity']) - float(trader.portfolios()['market_value'])