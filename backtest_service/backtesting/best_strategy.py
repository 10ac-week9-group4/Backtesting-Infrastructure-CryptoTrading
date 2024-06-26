import yfinance as yf
import sys
import pandas as pd
import backtrader as bt
from datetime import datetime
from backtrader.feeds import PandasData
from backtrader.analyzers import Returns, DrawDown, SharpeRatio

# Import strategies
sys.path.append('../../')
from src.strategies.Test_Strategy import TestStrategy
from src.strategies.SMA import SMA
from src.strategies.SMA_RSI import SMA_RSI
from src.strategies.SMA_CrossOver import SmaCrossOver
from src.strategies.MovingAverageCrossoverStrategy import MovingAverageCrossoverStrategy

from src.backtesting.run_backtest import run_backtest,prepare_cerebro,run_test

def score_strategy(returns, drawdown, sharpe_ratio):
    # Extract numeric values from OrderedDict
    returns_value = returns['rtot']
    drawdown_value = drawdown['max']['drawdown']
    sharpe_ratio_value = sharpe_ratio['sharperatio']

    # Ensure drawdown_value is not zero to avoid division errors
    if drawdown_value == 0:
        drawdown_value = 1e-6  # small value to prevent division by zero
    
    #average score
    return 0.4 * returns_value + 0.4 * (1 / drawdown_value) + 0.2 * sharpe_ratio_value

def select_best_strategy(strategies, data):
    #initialized to negative infinity
    best_score = -float('inf')
    best_strategy = None
    
    for strategy in strategies:
        returns, drawdown, sharpe_ratio = run_backtest(strategy, data)
        score = score_strategy(returns, drawdown, sharpe_ratio)
        
        if score > best_score:
            best_score = score
            best_strategy = strategy
    
    return best_strategy

def main():
    # Load or download data (example using yfinance)
    asset = 'GOOGL'
    start_date = '2015-01-01'
    end_date = datetime.now().strftime("%Y-%m-%d")
    data = yf.download(asset, start=start_date, end=end_date)
    
    strategies = [TestStrategy, SMA, SMA_RSI, SmaCrossOver, MovingAverageCrossoverStrategy]
    best_strategy = select_best_strategy(strategies, data)
    
    print(f"The recommended strategy is: {best_strategy.__name__}")

if __name__ == "__main__":
    main()

