# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 10:40:13 2017

@author: Tom
"""
from pandas.io.data import DataReader

Tickers = [
    "HK3188"
];
        
for ticker in Tickers:
    try:
        data = DataReader(ticker, 'yahoo')
        print(data.head())
    except Exception as e:
        print("{} failed. {}\n".format(ticker, e))        