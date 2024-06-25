# cerebro=prepare_cerebro('BTC',TestStrategy,"../data/BTC-USD.csv","2024-04-19","2024-06-19")
import yfinance as yf
import pandas as pd
import backtrader as bt
from datetime import datetime
import os
import sys
import json
# from backtrader.analyzers import Returns,DrawDown,SharpeRatio,TradeAnalyzer

# import strategies
sys.path.append('../../')
from src.strategies.Test_Strategy import TestStrategy
from src.strategies.SMA import SMA
from src.strategies.SMA_RSI import SMA_RSI
from src.strategies.SMA_CrossOver import SmaCrossOver
from src.strategies.MovingAverageCrossoverStrategy import MovingAverageCrossoverStrategy

from src.backtesting.run_backtest import run_test, prepare_cerebro

'''{
  "asset": "AAPL",
  "strategy": "SMA_RSI",
  "start_date": "2018-12-19",
  "end_date": "2024-06-19",
  "cash": 100000,
  "commission": 0.005
}'''
{
  "asset": "AAPL",
  "strategy": "MovingAverageCrossoverStrategy",
  "start_date": "2018-12-19",
  "end_date": "2024-06-19",
  "cash": 100000,
  "commission": 0.005
}


cerebro=prepare_cerebro('GOOGL',MovingAverageCrossoverStrategy,"../data/BTC-USD.csv","2006-12-19","2024-06-19", 100000, 0.005)

result=run_test(cerebro)
print(result)