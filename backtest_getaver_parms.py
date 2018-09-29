#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  8 20:43:37 2018

@author: robben
"""

from basic import *
from position_update import * 
from portfolio import *

def back_test_get_aver_params(backtest_start, backtest_end, pc_lookback_windows, param_lookback_windows, n, uni_ret):
    backtest_time = uni_ret.index[uni_ret.index <= backtest_end]
    backtest_time = backtest_time[backtest_time >= backtest_start]
    backtest_time = backtest_time.strftime('%Y%m%d')
    
    result_df = pd.DataFrame()
    for ticker in uni_ret.columns:               
        result = pd.DataFrame()
        ADF = []
        
        for time in backtest_time:
            testset_ret = uni_ret.truncate(after = time)
            stock_ret = testset_ret[ticker]
            #111111111111
            r = resi(n, testset_ret, stock_ret, pc_lookback_windows, param_lookback_windows)
            OU_X = r.cumsum()
            ADF += [test_stationarity(OU_X, 0.1)]
            params = signal_gen(OU_X)
            result = pd.concat([result, params], ignore_index = True)
        
        plt.plot(result['s-score'], label = ticker)
        plt.legend(loc = 'upper left')
        
        #calculate the mean of those parameters, i.e. s-score.
        params_mean = pd.DataFrame([result.mean()], index = [ticker], columns = result.columns)
        ADF_mean = pd.DataFrame(pd.DataFrame(ADF).mean())
        ADF_mean.index = [ticker]
        ADF_mean.columns = ['%Stationary']
        params_mean = pd.concat([params_mean, ADF_mean], axis = 1)
        #put those parameters from different stocks together
        result_df = pd.concat([result_df, params_mean])
    return result_df

def back_test_etf_get_aver_params(backtest_start, backtest_end, etf_ret, uni_ret, param_lookback_windows):
    backtest_time = uni_ret.index[uni_ret.index <= backtest_end]
    backtest_time = backtest_time[backtest_time >= backtest_start]
    backtest_time = backtest_time.strftime('%Y%m%d')
    
    result_df = pd.DataFrame()
    for ticker in uni_ret.columns:               
        result = pd.DataFrame()
        
        ADF = []
        for time in backtest_time:
            testset_ret = uni_ret.truncate(after = time)
            test_etf_ret = etf_ret.truncate(after = time)
            stock_ret = testset_ret[ticker]
    
            param_lookback_etf_ret = test_etf_ret[-param_lookback_windows:]
            param_lookback_stock_ret = stock_ret[-param_lookback_windows:]
            
            B, alpha = regr(param_lookback_etf_ret, param_lookback_stock_ret)
            r = -param_lookback_etf_ret.dot(B) - alpha + param_lookback_stock_ret
            
            OU_X = r.cumsum()
            ADF += [test_stationarity(OU_X, 0.1)]
            params = signal_gen(OU_X)
            result = pd.concat([result, params], ignore_index = True)
#        s_score_df = pd.DataFrame([result['s-score']], index = backtest_time)
#        
#        s_score_df.plot()
#        plt.legend(loc = 'upper left')
#            plt.plot(OU_X)
#        plt.plot(result['s-score']) 
        ADF_mean = pd.DataFrame(pd.DataFrame(ADF).mean())
        ADF_mean.index = [ticker]
        ADF_mean.columns = ['%Stationary']
        #calculate the mean of those parameters, i.e. s-score.
        params_mean = pd.DataFrame([result.mean()], index = [ticker], columns = result.columns)
        params_mean = pd.concat([params_mean, ADF_mean], axis = 1)
        plt.plot(result['beta'], label = 'AR1 Beta')
        plt.plot(ADF, 'r.', label = 'ADF result')
        plt.legend(loc = 'center left')
        #put those parameters of different stocks together
        result_df = pd.concat([result_df, params_mean])####应该是params_mean
    return result_df


