# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 10:40:13 2017

@author: Tom
"""

import datetime as dt
import pickle
#import matplotlib.pyplot as plt 
#import numpy as np 
#import numpy.linalg as la 
import pandas as pd
#import scipy.cluster.hierarchy as sch
#import seaborn as sns
from pandas.io.data import DataReader
#from scipy.stats import mode 
#from scipy.stats.stats import pearsonr
#from nearest_correlation import nearcorr
#from IPython.display import Image
#from cvxpy import Variable, Minimize, quad_form, Problem, sum_entries, norm
#%matplotlib inline

#style.use('ggplot')

#import sys
#sys.path.append('C:\\git\\AutomatedInvestments')
import data
import os.path


tickerdf = pd.read_csv('AssetUniverse.csv')    
tickers = tickerdf['Ticker']                 # extract list of tickers from dataframe


if(not os.path.exists('start_dates.pkl') or not os.path.exists('close_price.pkl')):
    close_prices, start_dates = data.load_historical_prices(tickers, verbose=True)

    with open('start_dates.pkl', 'w+') as f_start_dates:
        pickle.dump(start_dates, f_start_dates)             
    close_prices.to_pickle('close_price.pkl')              
else:
    close_prices = pd.read_pickle('close_price.pkl')
    with open('start_dates.pkl') as f_start_dates:
        start_dates = pickle.load(f_start_dates) 

max(x, key=lambda i: x[i])        