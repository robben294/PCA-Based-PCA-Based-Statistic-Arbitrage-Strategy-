#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 17:27:23 2018

@author: robben
"""

from basic import *
from position_update import * 
from portfolio import *

"""
Back testing 
"""

def back_test_etf(backtest_start, backtest_end, etf_ret, uni_ret, param_lookback_windows):
    backtest_time = uni_ret.index[uni_ret.index <= backtest_end]
    backtest_time = backtest_time[backtest_time >= backtest_start]
    backtest_time = backtest_time.strftime('%Y%m%d')
    
    s_pd = pd.DataFrame()
    for i in range(len(backtest_time)-1):

        if i == 0:
            # Create empty portfolio at first circulation
            portfolio = pd.DataFrame(np.zeros(len(uni_ret.columns)), index = uni_ret.columns, columns = [backtest_time[1]])
            portfolio = portfolio.astype('int')
            # Concat a new column the same as the day before
        else:
            portfolio = pd.concat([portfolio, portfolio.iloc[:,-1]], axis = 1)
            portfolio.columns.values[-1] = backtest_time[i+1]

        testset_ret = uni_ret.truncate(after = backtest_time[i])
        test_etf_ret = etf_ret.truncate(after = backtest_time[i])
            
        s_list = pd.DataFrame()
        for ticker in uni_ret.columns:
            stock_ret = testset_ret[ticker]

            param_lookback_etf_ret = test_etf_ret[-param_lookback_windows:]
            param_lookback_stock_ret = stock_ret[-param_lookback_windows:]
            
            B, alpha = regr(param_lookback_etf_ret, param_lookback_stock_ret)
            r = -param_lookback_etf_ret.dot(B) - alpha + param_lookback_stock_ret
            
            OU_X = r.cumsum()
            params = signal_gen(OU_X)
            s = pd.DataFrame(params['s-score'])
            s.index = [ticker]
            s.columns = [backtest_time[i]]
            s_list = pd.concat([s_list, s])
            
        s_pd = pd.concat([s_pd, s_list], axis = 1)
        position_update(portfolio, s_list)
        
    return portfolio, s_pd

def back_test(backtest_start, backtest_end, pc_lookback_windows, param_lookback_windows, n, uni_ret):
    backtest_time = uni_ret.index[uni_ret.index <= backtest_end]
    backtest_time = backtest_time[backtest_time >= backtest_start]
    backtest_time = backtest_time.strftime('%Y%m%d')
    
    hedge_pd = pd.DataFrame()
    for i in range(len(backtest_time)-1):

        if i == 0:
            # Create empty portfolio at first circulation
            portfolio = pd.DataFrame(np.zeros(len(uni_ret.columns)), index = uni_ret.columns, columns = [backtest_time[1]])
            portfolio = portfolio.astype('int')
            # Concat a new column the same as the day before
        else:
            portfolio = pd.concat([portfolio, portfolio.iloc[:,-1]], axis = 1)
            portfolio.columns.values[-1] = backtest_time[i+1]
            
        testset_ret = uni_ret.truncate(after = backtest_time[i])
    
        s_list = pd.DataFrame()
        hedge_list = pd.DataFrame()
        for ticker in uni_ret.columns:   
            stock_ret = testset_ret[ticker]
            
            r, ei_port = resi(n, testset_ret, stock_ret, pc_lookback_windows, param_lookback_windows)
            OU_X = r.cumsum()
            params = signal_gen(OU_X)            
            s = pd.DataFrame(params['s-score'])
            s.index = [ticker]
            s.columns = [backtest_time[i]]
            s_list = pd.concat([s_list, s])
            
            hedge = pd.DataFrame([ei_port])
            hedge.columns = [ticker]
            hedge.index = [backtest_time[i]]
            hedge_list = pd.concat([hedge_list, hedge], axis = 1)
            
        position_update(portfolio, s_list)
        print(backtest_time[i])
        
        hedge_pd = pd.concat([hedge_pd, hedge_list])
        
    result = portfolio
    return result, hedge_pd
    