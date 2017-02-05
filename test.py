# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 10:40:13 2017

@author: Tom
"""
from pandas.io.data import DataReader

Tickers = [
    "CRUD"
    "IEMU"
    "IUKD"
    "IUSA"
    "SLXX"
    "H50E"
    "S600"
    "VUSA"
];
        
for ticker in Tickers:
    data = DataReader(ticker, 'yahoo')
    print(data.head())        