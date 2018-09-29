#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 17:22:52 2018

@author: robben
"""

from basic import *

def sell_close_operator(x):
    if x == -1:
        return -1
    else:
        return 0
    
def buy_close_operator(x):
    if x == 1:
        return 1
    else:
        return 0
    
def long_only_operator(x):
    if x == 1:
        return 1
    else:
        return 0

def buy_open_update(portfolio, buy_open):
    # the buy_open straight inside need to be a SERIES to get a empty dataframe if no value satisfy
    stock_query = buy_open[buy_open.iloc[:,-1] == 1].index  # Find out the index that need to be bought open
    portfolio.iloc[:,-1].loc[stock_query] = 1 # Let stock position become 1
    
def sell_open_update(portfolio, sell_open):
    stock_query = sell_open[sell_open.iloc[:,-1] == 1].index  # Find out the index that need to be bought open
    portfolio.iloc[:,-1].loc[stock_query] = -1
    
def sell_close_update(portfolio, sell_close):
    stock_query = sell_close[sell_close.iloc[:,-1] == 1].index  # Find out the index that need to be bought open
    portfolio.iloc[:,-1].loc[stock_query] =  portfolio.iloc[:,-1].loc[stock_query].apply(lambda x: sell_close_operator(x))
    
def buy_close_update(portfolio, buy_close):
    stock_query = buy_close[buy_close.iloc[:,-1] == 1].index  # Find out the index that need to be bought open
    portfolio.iloc[:,-1].loc[stock_query] =  portfolio.iloc[:,-1].loc[stock_query].apply(lambda x: buy_close_operator(x))

    
def position_update(portfolio, s_list):
    buy_open = (s_list < -1.25).astype('int')
    sell_open = (s_list > 1.25).astype('int')
    sell_close = (s_list > -0.75).astype('int')
    buy_close = (s_list < 0.75).astype('int')
    
    sell_close_update(portfolio, sell_close)
    buy_close_update(portfolio, buy_close)
    buy_open_update(portfolio, buy_open)
    sell_open_update(portfolio, sell_open)
    
    
def long_only(portfolio):
    portfolio.iloc[0,:] = portfolio.iloc[0,:].apply(lambda x: long_only_operator(x))