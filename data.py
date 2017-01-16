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