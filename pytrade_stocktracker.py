import pytrade_stockanalysis as sa
import pytrade_robinhood as rh
import pandas as pd
import csv

## build an empty dataframe to store stock analysis data
df_columns = ['Last Price', 'Price with Returns', 'Expected Price', 'Recommended Position', 'Stock Owned', 'Stock Price Slope', 'Percent around Expected', 'Volatility', 'Average Volume']
stock_price_limit = 100
average_volume_limit = 1000000


def compile_stock_analysis():    
    stock_datas = []
    stock_symbols = []
    owned_securities = rh.find_owned_securities()
    with open('sp500.csv', 'r') as sp_companies:
        csv_reader = csv.reader(sp_companies)
        for company in csv_reader:
            stock_df = sa.pull_stock_data(company[0])
            if not stock_df.empty:
                rec_pos, last_price, expected_price, price_with_returns, price_slope, volatility, average_volume = sa.grade_stock(stock_df)
                perc_to_expected = ((price_with_returns - expected_price) / expected_price)
                stock_owned = company[0] in owned_securities.index
                stock_datas.append([last_price, price_with_returns, expected_price, rec_pos, stock_owned, price_slope, perc_to_expected, volatility, average_volume])
                stock_symbols.append(company[0])
    df_stk_analysis = pd.DataFrame(stock_datas, index=stock_symbols, columns = df_columns)
    return df_stk_analysis

def find_potential_positions():
    df = compile_stock_analysis()
    df_filtered = df[(df['Stock Owned'] == False) 
                    & (df['Recommended Position'] == 'Buy') 
                    & (df['Last Price'] < stock_price_limit)
                    & (df['Average Volume'] > average_volume_limit)]
    return df_filtered.sort_values(by='Volatility', ascending = True)