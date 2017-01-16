# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 19:33:51 2017

@author: Tom
"""
import pandas as pd
import quandl

auth = "d85AxYgsEaWPyhx_k2ZL"

def load_historical_prices(tickers, verbose = False):
    start_dates = {}
    ticker_df_list = []                       # initialize list of dataframes for each ticker                          #
    
    for ticker in tickers: 
        try:
            r = quandl.get("LSE/{0}".format(ticker), authtoken=auth)
            r['Ticker'] = ticker 
            start_dates[ticker] = r.index.values[0];
            ticker_df_list.append(r)
            if verbose:
                print("Obtained data for ticker %s" % ticker)
        except:
            if verbose:
                print("No data for ticker %s" % ticker)
    
    df = pd.concat(ticker_df_list)        # build single df of all data
    cell= df[['Ticker','Price']]          # extract ticker and close price information 
    cell.reset_index().sort(['Ticker', 'Date'], ascending=[1,0]).set_index('Ticker')
    
    return cell, start_dates
    
def get_pricing(symbols, start_date, verbose = True):
    ticker_df_list = []
    for index, row in symbols.iterrows(): 
        try:
            r = quandl.get(row.Quandl.format(row.Ticker), start_date=start_date, authtoken=auth)
            r['Ref'] = row.Ticker 
            r = r.loc[:, ['Ref', row.PriceColumn]]
            r.rename(columns={row.PriceColumn: 'Price'}, inplace=True)
            ticker_df_list.append(r)
            if verbose:
                print("Obtained data for ticker %s" % row.Ticker)
        except Exception as e:
            if verbose:
                print("No data for ticker %s\n%s" % (row.Ticker, str(e)))    
    df = pd.concat(ticker_df_list)   
    cell= df[['Ref','Price']]     
    #cell.reset_index().sort(['Ref', 'Date'], ascending=[1,0]).set_index('Ref')
    
    return cell.pivot(columns='Ref')
