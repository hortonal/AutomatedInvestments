# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 11:28:01 2017

@author: Tom
"""
import sys
import data_fns
from optimize_fns import *
from pandas_datareader import data
import pandas as pd
from PyQt5.QtWidgets import (QMainWindow, QLabel, QAction, QFileDialog, QApplication, QPushButton)
from PyQt5.QtGui import (QIcon)
from PyQt5.QtCore import (Qt)
import os
import pickle as pkl
import operator

class Launchpad(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.initUI()
        
    def initUI(self):      
        self.btnUniverse = QPushButton('Load Asset Universe', self)
        self.btnUniverse.move(50, 50)
        self.btnUniverse.resize(200,40)
        self.btnUniverse.clicked.connect(self.openAssetUniverse)  

        self.txtUniverse = QLabel(self)
        self.txtUniverse.move(260, 50)
        self.txtUniverse.resize(400,40)
  
        self.btnPrices = QPushButton('Load Historic Prices', self)
        self.btnPrices.move(50, 100)
        self.btnPrices.resize(200,40)
        self.btnPrices.clicked.connect(self.loadHistoricPrices)    
        
        self.txtUniverseStatus = QLabel(self)
        self.txtUniverseStatus.move(260, 100)
        self.txtUniverseStatus.resize(400,40)
  
        self.btnOptimize = QPushButton('Mean Variance Optimize', self)
        self.btnOptimize.move(50, 150)
        self.btnOptimize.resize(200,40)
        self.btnOptimize.clicked.connect(self.meanVarianceOptimization)    
 
        self.setGeometry(300, 300, 710, 300)
        self.setWindowTitle('File dialog')
        self.show()
        
    def openAssetUniverse(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'Universe/AssetUniverse.csv')

        if fname[0]:
            self.txtUniverse.setText(os.path.relpath(fname[0]))        
            self.symbols = pd.read_csv(fname[0])
        else:
            self.txtUniverse.setText("Select Asset Universe File")       
        
        self.update_cache_status()
            
    def loadHistoricPrices(self):
        #QApplication.setOverrideCursor(Qt.WaitCursor)
        fixings, start_dates = data_fns.yahoo_prices(self.symbols, start_date='1970-01-01')
        #QApplication.restoreOverrideCursor()
        fixings.to_pickle(self.get_cache_name())   
        pkl.dump(start_dates, open(self.get_start_cache_name(), "wb"))
        self.update_cache_status()
        
    def meanVarianceOptimization(self):
        fixings_sparse = pd.read_pickle(self.get_cache_name())
        start_dates = pkl.load(open(self.get_start_cache_name(), "rb"))
        fixings = fixings_sparse[fixings_sparse.index >= max(start_dates.values())]
        # Do we want to resample to just weekly/monthly fixings?
        resample = fixings.resample('W-MON').mean()
        rets = resample.pct_change(fill_method='pad')
        
        sol = mean_variance(rets)
        plot_portfolios(rets, sol)
        plot_weights(rets, [x for x in sol if x['sd'] > 0.02][0])

    def get_cache_name(self):
        return os.path.normpath('Pickle/' + self.txtUniverse.text().replace(".csv", ".pkl").translate(
                                str.maketrans({"\\":  r"-", "/":  r"-"})))
    
    def get_start_cache_name(self):
        return self.get_cache_name().replace(".pkl", "_starts.pkl")

    def update_cache_status(self):
        if os.path.exists(self.get_cache_name()) and os.path.exists(self.get_start_cache_name()):
            start_dates = pkl.load(open(self.get_start_cache_name(), "rb"))
            status = 'Cached. Max start date: {}'.format(max(start_dates.items(), key=operator.itemgetter(1))) 
        else:
            status = 'Nothing Cached @ {}'.format(self.get_cache_name())
        
        self.txtUniverseStatus.setText(status)

                    
        
if __name__ == '__main__':
    app = 0
    app = QApplication(sys.argv)
    ex = Launchpad()
    sys.exit(app.exec_())