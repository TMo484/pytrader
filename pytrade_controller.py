import pytrade_robinhood as rh
import pytrade_stocktracker as st
import pytrade_stockanalysis as sa
import math
import datetime as dt
from time import sleep

## 0 = uninitialized; 1 = trading time; 2 = markets closed; 3 = sleeping; 4 = outside prime trading time
pat_status = 0

min_cash_available = 1000
max_position_value = 100
wait_until_time = None


def check_time_limits(start_time, end_time):
   now = dt.datetime.today() 
   if now.weekday() <= 4 and dt.time(start_time[0], start_time[1]) <= now.time() <= dt.time(end_time[0], end_time[1]):
       return True
   else:
       return False
           

def has_available_cash():
    cash = rh.find_available_cash()
    if cash > min_cash_available:
        return True
    else:
        return False

## find the next best position to take 
def find_next_position(potential_positions_df):
    next_position = potential_positions_df.iloc[0]
    return next_position

def take_next_position(next_position):
    ticker = next_position.name
    num_shares = math.floor(max_position_value / next_position['Last Price'])
## Enter Tracking here
    rh.buy_order(ticker, num_shares)
    return ticker, num_shares
    

def find_stocks_to_sell():
    df_stocks = rh.find_owned_securities()
    stocks_to_sell = []
    for i in df_stocks.index:
        stock_data = df_stocks.loc[i]
        if stock_data['Shares Held'] > stock_data['Shares Pending Sale']:
            stocks_to_sell.append(stock_data)            
    return stocks_to_sell
    

def do_work():
    global pat_status
    try:
        if pat_status == 0:
            if pat_status == 0:
                print("**yawn** Hello there! Let's see what we got going on.")
            if check_time_limits((9,30), (11,00)):
                print("*DING DING DING* Looks like we're in trading time! Let's make some money!")
                pat_status = 1
            elif check_time_limits((9,30), (4,00)):
                print("Hmmm.. Looks like the markets are open, but outside prime hours. I'll rest for a while.")
                pat_status = 4
            else:
                print("Looks like the markets are closed.")
                pat_status = 2
                
        elif pat_status == 1: 
            if has_available_cash():
                available_cash = rh.find_available_cash()
                print("Looks like I have ${0}, to play with".format(available_cash))
                print("Finding some potential positions")
                df_potential_positions = st.find_potential_positions()
                next_position = find_next_position(df_potential_positions)
                ticker, num_shares = take_next_position(next_position)
                print("Position taken {0} shares of {1}".format(num_shares, ticker))
                print("That was exhausting! I'm gonna give it 10 min before I run again.")
                sleep(600)
            else:
                print("I'm out of cash to spend.. I'll wait 10 min and check in")
                sleep(600)
        
        elif pat_status == 2:
            stocks_for_sale = []
            stocks_for_sale = find_stocks_to_sell()
            if stocks_for_sale != []:
                print("Looks like we got some stocks to sell! Initiating sell orders.")
                for stock in stocks_for_sale:
                    ticker = stock.name
                    sell_price = float("{:.2f}".format(float(stock['Buy Price']) * (1 + sa.target_return)))
                    instrument = stock['Stock Instrument']
                    num_shares = float(stock['Shares Held'])
                    print("Placing limit sell order for {0} shares of {1}, at a price of {2}".format(num_shares, ticker, sell_price))
                    rh.sell_order(ticker, instrument, num_shares, 'limit', sell_price, 'GTC')
                    pat_status = 3
            else:
                print("No stocks to sell today. I'll sleep till the markets are open.")
                pat_status = 3
        
        elif pat_status == 3:
            print("...zzzzzz...")
            sleep(10)
            
        elif pat_status == 4:
            print("Just checked.. Still waiting for the markets to close")
            sleep(10)

            
    except KeyboardInterrupt:
        print("Okay, I'll stop doing that now")