#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 11:02:29 2018

@author: robben
"""

from basic import * 
from position_update import *
from portfolio import *
from back_test import *

#pdr.get_data_yahoo('AAPl')
#start = datetime.datetime(2018,6,5)
#end = datetime.datetime(2018,6,6)
#data.DataReader("SPY", "yahoo", start, end)
#stock = yf.download('SPY', start, end)
tickers = ['XLK', 'XLE', 'XLF', 'XLY', 'XLI', 'XLB', 'XLV', 'XLU', 'XLP']
start = "2016-01-01"
end = "2017-01-01"

    
"""
Step 3: Calculate residual
"""
n = 5
pc_lookback_windows = 250
param_lookback_windows = 60

"""
Plot/ Compare market portfolio(using SPY) with PC1
"""
#Get SPY data and plot
spy = get_data(["SPY"], start, end)
plot_cum_ret([cal_ret(spy),pro_ret[:,0]])
plot_cum_ret([ei_port["PC1"]])
plot_cum_ret([ei_port_norm['PC1']])
plot_cum_ret([pro_ret[:,0]])

"""
Download XLF/JPM data; Test the simplest model
"""
xlf_price = get_data(['XLF'], '2005-01-01', '2018-01-01')
xlf_ret = cal_ret(xlf_price)
xlf_log_ret = cal_log_ret(xlf_price)
jpm_price = get_data(['JPM'], '2005-01-01', '2018-01-01')
jpm_ret = cal_ret(jpm_price)
jpm_log_ret = cal_log_ret(jpm_price)
jpm_portfolio = back_test_etf('2006-01-01', '2018-01-01', xlf_ret, jpm_ret, param_lookback_windows)
jpm_portfolio.to_csv('/Users/robben/desktop/new.csv')
calculate_portfolio_return(jpm_portfolio, construct_trading_portfolio(jpm_ret, xlf_ret))
jpm, s = back_test_etf('2006-01-01', '2008-01-01', xlf_ret, jpm_ret, param_lookback_windows)
s.to_csv('/Users/robben/desktop/s.csv')

etf_test('2013-01-01', '2018-09-13', 'XLK', 'FB', param_lookback_windows, long_only_ = True, hedge_ = False)

backtest_start = '2010-03-01'
backtest_end = '2018-01-01'
price_10_18 = get_data(tickers, '2010-01-01', '2018-01-01')
#ret_10_18 = cal_ret(price_10_18)
log_ret_10_18 = cal_log_ret(price_10_18)
ret_10_18 = cal_ret(price_10_18)
etf_portfolio, hedge = back_test(backtest_start, backtest_end, pc_lookback_windows, param_lookback_windows, n, ret_10_18)
calculate_portfolio_return(etf_portfolio, (ret_10_18 - hedge).dropna())

