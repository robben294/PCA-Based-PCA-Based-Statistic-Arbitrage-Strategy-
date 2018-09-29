#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 16:12:59 2018

@author: robben
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from pandas_datareader import data, wb
import pandas_datareader as pdr
import fix_yahoo_finance as yf
import datetime 
from sklearn.decomposition import PCA
from sklearn import linear_model
import scipy.linalg as la
from pandas.tools.plotting import autocorrelation_plot
import math
from statsmodels.tsa.stattools import adfuller


"""
Step 1: Get data from yahoo finance and save in a pandas.dataframe
"""
#Imput must be a list
def get_data(tickers, start, end):
    dates = pd.date_range(start, end)
    stocks = pd.DataFrame(index = dates)
    yf.pdr_override()
    for ticker in tickers:
        stock = pdr.data.get_data_yahoo(ticker, start = start, end = end)
        stock = stock.rename(columns = {"Adj Close" : ticker})
        stocks = stocks.join(stock[ticker])
    stocks = stocks.dropna()
    return stocks

def cal_ret(dataframe):
    ret = dataframe.pct_change(1).dropna()
    return ret
    
def cal_log_ret(dataframe):
    ret = dataframe.pct_change(1).dropna()
    ret = ret + 1
    log_ret = np.log(ret)
    return log_ret

#Imput return
def cal_cum_ret(ret):
    ret_idx = ret + 1
    ret_idx = ret_idx.cumprod()
    return ret_idx
    

"""
Step 2: Pca method
"""
def pca1(n, dataframe): 
    pca = PCA(n_components = n)
    pca.fit(dataframe)
    pro_ret = pca.fit_transform(dataframe)
#    print(pca.components_)
#    print(pca.explained_variance_ratio_)
#    plt.bar(range(n), pca.explained_variance_ratio_)
#    plt.title('variance explained by pc')
#    plt.show()
    pc = pd.DataFrame(index = dataframe.columns)
    for i in range(len(pca.components_)):
        idx = 'PC' + str(i+1)
        pc[idx] = pca.components_[i]
    return [pc, pro_ret]

def plot_cum_ret(rets):
    for i in range(len(rets)):
        cum = cal_cum_ret(rets[i])
        plt.plot(range(len(cum)), cum, label = "cumulative return" + str(i))
        plt.legend(loc = 'best')
        plt.xlabel(rets.index)
    plt.show()


#Function for regression and return beta and intercept  
def regr(X, y):
    regr = linear_model.LinearRegression()
    regr.fit(X, y)
    b = regr.coef_
    a = regr.intercept_
    return ([b, a])
    
#using eigen value decomposition
def evd():
    ret_norm = (sec_ret - sec_ret.mean())
    u, v = la.eig(ret_norm.cov())
#    v = np.mat(v).I
    ix = np.argsort(-u)
    for i in range(len(ix)):
        print("\n PC", i, ":", v[:, ix[i]])
        
## TS related functions
def test_stationarity(ts, level):
    """
    ts: a time series, ndarray or array
    level: a float, options are 0.01, 0.05, 0.1
    Test wether the time-series is stationary or not
    H0: There is a unit root (Non- stationary)
    
    returns True when it's stationary and False when it's not stationary
    """
    adf = adfuller(ts)
    return (adf[1] < level)

def resi(n, uni_ret, stock_ret, pc_lookback_windows, param_lookback_windows):
    """
    Function that calculate the residual: portfolio return(PCs as each stock) - stock return
    Using regression method to get the beta and intercept.

    Input: n: for PCA. 
        stock_ret: one of the stock return(pd.dataframe) for regression, on left hand side
        uni_ret: All stocks in the stock universe's return 
    """
    uni_ret = uni_ret[-pc_lookback_windows:]  #shape:  pc_look_back_windows * len(uni_ret.columns)
                                                # 252 * 9
    param_lookback_uni_ret = uni_ret[-param_lookback_windows:] # 60 * 9 
    param_lookback_stock_ret = stock_ret[-param_lookback_windows:] # 60 * 9
        
    pc = pca1(n, uni_ret)[0] # shape: 9 * 5 (len(uni_ret.columns) * n)
    ei_port = param_lookback_uni_ret.dot(pc) # (60 * 9) * (9 * 5) = 60 * 5
                                            # shape: pc_lookback_windoes * n
    B, alpha = regr(ei_port, param_lookback_stock_ret)
    resi = -ei_port.dot(B) - alpha + param_lookback_stock_ret
    ######################33
    hedge = ei_port.dot(B) # a series, not dataframe

    # shape of ei_port.dot(B): (60 * 5) * (5 * 1)  = 60 * 1
    return resi, hedge.iloc[-1]

def hedge_portfolio(start, end, pc_lookback_windows, param_lookback_windows, n, uni_ret):
    """
    Calculate hedging portfolio return.
    
    Input: start date and end date
            pc lookback windows: to get principal components.
            parameter lookback windows: to get beta and alpha. Only use parameter lookback windows for regression
    """
    uni_ret = uni_ret[-pc_lookback_windows:]


def signal_gen(OU_X):
    """
    Input: OU_X: Residual process(sum of residual)
            ticker: stock from which residual 
    Output: mainly s-score, also other parameters
    """
    X = np.array(OU_X.shift(1)[1:]).reshape(-1,1)
    y = np.array(OU_X[1:]).reshape(-1,1)
    b, a = regr(X,y)
    eta = X.dot(b) + a - y  # residual 
    
    kappa = -math.log(b) * 252
    m = a / (1 - b)
    sigma = math.sqrt(np.var(eta) * 2 * kappa / (1 - b**2))
    sigma_eq = sigma / math.sqrt(2 * kappa)
    s_score = -m / sigma_eq
    
    df = pd.DataFrame({'kappa' : [kappa], 'beta' : [b], 'alpha' : [a], 'm' : [m], 's-score' : [s_score], 'sigma_eq' : [sigma_eq]})
    return df
    
