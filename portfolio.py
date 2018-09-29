#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 17:25:14 2018

@author: robben
"""
from basic import *

def construct_trading_portfolio(stock_ret, hedge_portfolio):
    """
    This is just for jpm and xlf.
    If we consider etfs, we can minus them directly.
    """
    for i in range(len(stock_ret.columns)):
        stock_ret.iloc[:,i] = stock_ret.iloc[:,i] - hedge_portfolio.iloc[:,0]
    return stock_ret

def calculate_portfolio_return(portfolio, stock_ret):
    stock_num = len(portfolio.index)#############
    
    use_ret = stock_ret.truncate(before = portfolio.columns[0])
    use_ret = use_ret.iloc[0:len(portfolio.columns), :]
    daily_stock_ret = portfolio.T * use_ret #daily_ret is a DataFrame including each stock
    daily_ret = ((1/stock_num) * daily_stock_ret).sum(axis = 1)
    
    mean = daily_ret.mean()
    std = daily_ret.std()
    
    cumulative_ret = cal_cum_ret(daily_ret).dropna()  #This is a DataFrame with cumulatative return of every day
    plt.plot(cumulative_ret)
    
    return mean, std, (cumulative_ret[-1] - 1), cumulative_ret

def etf_test(start, end, etf, stock, param_lookback_windows, long_only_, hedge_):
    etf_price = get_data([etf], start, end)
    etf_ret = cal_ret(etf_price)
    stock_price = get_data([stock], start, end)
    stock_ret = cal_ret(stock_price)
    
    backtest_time = datetime.datetime.strptime(start, '%Y-%m-%d') + datetime.timedelta(param_lookback_windows)
    backtest_time = backtest_time.strftime('%Y-%m-%d')
    
    stock_portfolio, s = back_test_etf(backtest_time, end, etf_ret, stock_ret, param_lookback_windows)
    if long_only_ == True:
        long_only(stock_portfolio)
    if hedge_ == True:
        calculate_portfolio_return(stock_portfolio, construct_trading_portfolio(stock_ret, etf_ret))
    if hedge_ == False:      
        calculate_portfolio_return(stock_portfolio, stock_ret)
        