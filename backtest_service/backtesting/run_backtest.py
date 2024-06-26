from datetime import datetime
from backtrader.analyzers import Returns,DrawDown,SharpeRatio,TradeAnalyzer
import yfinance as yf
import backtrader as bt
import os

from backtest_service.strategies import SmaCrossOver, SMA_RSI, SMA, Test_Strategy

# Get today's date as a string in the format YYYY-MM-DD
today_date_string = datetime.now().strftime("%Y-%m-%d")

def prepare_and_run_many_backtests(
        asset: str = "GOOGL",
        strategy = SmaCrossOver,
        strategy_params_list: list = [{}],  # List of dictionaries
        data_path: str = "../stock_data.csv",
        start_date: str = "2006-12-19",
        end_date: str = today_date_string,
        cash: int = 100000,
        commission: float = 0
    ) -> list:
    all_results = []  # Store results from each backtest
    for strategy_params in strategy_params_list:  # Iterate over each parameter set
        cerebro = prepare_cerebro(asset, strategy, data_path, start_date, end_date, cash, commission, **strategy_params)
        result = run_test(cerebro)
        all_results.append(result)
    return all_results


def prepare_and_run_backtest(
        asset:str="GOOGL",
        strategy=SmaCrossOver,
        strategy_params={},
        data_path:str="../stock_data.csv",
        start_date:str="2006-12-19",
        end_date:str=today_date_string,
        cash:int=100000,
        commission:float=0
  )->dict:
    cerebro = prepare_cerebro(asset,strategy,data_path,start_date,end_date,cash,commission, **strategy_params)
    result = run_test(cerebro)
    return result

def prepare_cerebro(asset,strategy,data_path,start_date:str,end_date:str=datetime.now(),cash:int=100000,commission:float=0,  **strategy_params)->bt.Cerebro:
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=commission)
    cerebro.addstrategy(strategy, **strategy_params)
    
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    # isExist = os.path.exists(data_path)
    # if not isExist:
    #     data = yf.download(asset,start_date,end=end_date)
        # data.to_csv(data_path)
    data = yf.download(asset,start_date,end=end_date)

    # Use PandasData to load DataFrame directly
    datafeed = bt.feeds.PandasData(
                    dataname=data,
                    fromdate=datetime.strptime(start_date, "%Y-%m-%d"),
                    todate=datetime.strptime(end_date, "%Y-%m-%d"),
              )

    cerebro.adddata(datafeed)
    # cerebro.addanalyzer(AnnualReturn)
    cerebro.addanalyzer(TradeAnalyzer)
    return cerebro

def run_test(cerebro:bt.Cerebro):

    result={}

    cerebro.addanalyzer(SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(Returns, _name='returns')
    cerebro.addanalyzer(DrawDown, _name='draw')
    cerebro.addanalyzer(TradeAnalyzer, _name='trade')
    
    starting = cerebro.broker.getvalue()
    res=cerebro.run()
    final=cerebro.broker.getvalue()

    thestrat = res[0]

    sharpe=thestrat.analyzers.sharpe.get_analysis()
    return_val=thestrat.analyzers.returns.get_analysis()
    drawdown=thestrat.analyzers.draw.get_analysis()
    trade=thestrat.analyzers.trade.get_analysis()

    result["sharpe_ratio"]=sharpe['sharperatio']
    result["return"]=return_val['rtot']
    result['max_drawdown'] = drawdown['max']['drawdown']
    result['win_trade'] = trade.get('won', {}).get('total', 'Undefined')
    result['loss_trade'] = trade.get('lost', {}).get('total', 'Undefined')
    result['total_trade'] = trade.get('total', {}).get('total', 'Undefined')
    result['start_portfolio'] = starting
    result['final_portfolio'] = final

    return result