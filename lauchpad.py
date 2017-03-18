# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 11:28:01 2017

@author: Tom
"""
#import matplotlib

# Make sure that we are using QT5
#matplotlib.use('Qt5Agg')

import sys
import data_fns
from optimize_fns import *
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QLabel, QFileDialog, QApplication, QPushButton, QSlider, QSizePolicy, QVBoxLayout, QWidget)
from PyQt5.QtCore import (Qt)
import os
import pickle as pkl
import operator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


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
        
        self.txtOptimizeStatus = QLabel(self)
        self.txtOptimizeStatus.move(260, 150)
        self.txtOptimizeStatus.resize(400,40)
        
        self.sliStandardDeviation = QSlider(Qt.Horizontal)
        #self.sliStandardDeviation.setMinimum(1)
        #self.sliStandardDeviation.setMaximum(1000)
        self.sliStandardDeviation.setValue(10)
        self.sliStandardDeviation.setTickPosition(QSlider.TicksBelow)
        self.sliStandardDeviation.setTickInterval(1)
        self.sliStandardDeviation.valueChanged.connect(self.standard_deviation_changed)
 
        self.txtTgtVol = QLabel(self)
        self.txtTgtVol.resize(400,40)

        self.dpi = 100
        self.fig = Figure((5.0, 6.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.axes = self.fig.add_subplot(111)

        self.canvas2 = FigureCanvas(self.fig)
        self.ops = self.fig.add_subplot(111, facecolor='green')

        self.main_widget = QWidget(self)
        l = QVBoxLayout(self.main_widget)
        l.addWidget(self.canvas2)
        l.addWidget(self.txtTgtVol)
        l.addWidget(self.sliStandardDeviation)
        l.addWidget(self.canvas)
        self.canvas.setParent(self.main_widget)

        self.main_widget.setFocus()
        self.main_widget.move(5, 250)
        self.main_widget.resize(3000,1150)
        
        self.setGeometry(300, 300, 3010, 1500)
        self.setWindowTitle('File dialog')
        self.show()
        
        self.optimization_solutions = []
        self.returns = pd.DataFrame()
        
        DefaultPath = 'Universe/AssetUniverse.csv'
        if os.path.exists(DefaultPath):
            self.txtUniverse.setText(os.path.relpath(DefaultPath))
            self.symbols = pd.read_csv(self.txtUniverse.text())
            self.update_cache_status()
        
    def openAssetUniverse(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', 'Universe/AssetUniverse.csv')

        if fname[0]:
            self.txtUniverse.setText(os.path.relpath(fname[0]))        
            self.symbols = pd.read_csv(self.txtUniverse.text())
        else:
            self.txtUniverse.setText("Select Asset Universe File")       
        
        self.update_cache_status()
            
    def loadHistoricPrices(self):
        #QApplication.setOverrideCursor(Qt.WaitCursor)
        fixings, start_dates = data_fns.yahoo_prices(self.symbols, start_date='1970-01-01')
        #QApplication.restoreOverrideCursor()
        fixings.to_pickle(self.get_cache_name())   
        pkl.dump(start_dates, open(self.get_start_cache_name(self.get_cache_name()), "wb"))
        self.update_cache_status()
        
    def meanVarianceOptimization(self):
        self.txtOptimizeStatus.setText("Optimization Running...")
        
        fixings_sparse = pd.read_pickle(self.get_cache_name())
        start_dates = pkl.load(open(self.get_start_cache_name(self.get_cache_name()), "rb"))
        fixings = fixings_sparse[fixings_sparse.index >= max(start_dates.values())]
        # Do we want to resample to just weekly/monthly fixings?
        resample = fixings.resample('W-MON').mean()
        self.returns = resample.pct_change(fill_method='pad')
        
        self.optimization_solutions = mean_variance(self.returns)
        self.optimization_solutions = sorted(self.optimization_solutions, key=lambda x: x['sd']);
        self.plot_portfolios(self.optimization_solutions)
        
        self.txtOptimizeStatus.setText("Optimization Complete")
        self.sliStandardDeviation.setMinimum(self.optimization_solutions[0]['sd']*1000)
        self.sliStandardDeviation.setMaximum(self.optimization_solutions[-1]['sd']*1000)
        self.standard_deviation_changed()

    def get_cache_name(self):
        return os.path.normpath('Pickle/' + self.txtUniverse.text().replace(".csv", ".pkl").translate(
                                str.maketrans({"\\":  r"-", "/":  r"-"})))
    
    def get_start_cache_name(self, cache):
        return cache.replace(".pkl", "_starts.pkl")

    def update_cache_status(self):
        if os.path.exists(self.get_cache_name()) and os.path.exists(self.get_start_cache_name(self.get_cache_name())):
            start_dates = pkl.load(open(self.get_start_cache_name(self.get_cache_name()), "rb"))
            status = 'Cached. Max start date: {}'.format(max(start_dates.items(), key=operator.itemgetter(1))) 
        else:
            status = 'Nothing Cached @ {}'.format(self.get_cache_name())
        
        self.txtUniverseStatus.setText(status)

    def plot_portfolios(self, sols):
        for i in sols:
            self.ops.plot(i['sd'], i['mean'], 'bs')
            
        p = self.returns.mean().as_matrix()
        covs = self.returns.cov().as_matrix()
        for i in range(len(p)):
            self.ops.plot(cvxpy.sqrt(covs[i,i]).value, p[i], 'ro')
            
        self.ops.set_xlabel('Standard deviation')
        self.ops.set_ylabel('Return')
        self.canvas2.draw()
        
    def draw_weights(self, sol):
        self.axes.clear()        
        self.axes.grid(1)
        objects = [x[1] for x in self.returns.columns.values];
        y_pos = np.arange(len(objects))
        self.axes.bar(y_pos, np.squeeze(np.asarray(sol['wgts'])))
        self.axes.set_xticks(y_pos+0.5)
        self.axes.set_xticklabels(objects, rotation='vertical')
        self.canvas.draw()
        
    def standard_deviation_changed(self):
        TgtVol = self.sliStandardDeviation.value()/1000
        self.txtTgtVol.setText("Target Vol: {}%".format(TgtVol*100))
        if len(self.optimization_solutions) > 0:
            # Find the nearest solution
            def sd_greater_than(tgt):
                def fil(sol):
                    sol['sd']>tgt
                return fil
                    
            #tgt_sd = sd_greater_than(self.sliStandardDeviation.value()/10000)
            #sol = next(filter(tgt_sd, self.optimization_solutions), None)
            for sol in self.optimization_solutions:
                if(sol['sd'] >= TgtVol):
                    self.draw_weights(sol)
                    break
        
if __name__ == '__main__':
    app = 0
    app = QApplication(sys.argv)
    ex = Launchpad()
    sys.exit(app.exec_())