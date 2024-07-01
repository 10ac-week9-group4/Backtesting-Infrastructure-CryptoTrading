from datetime import datetime
from backtrader.analyzers import Returns,DrawDown,SharpeRatio,TradeAnalyzer
import yfinance as yf
import backtrader as bt
import os
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import BDay
from datetime import timedelta
import yfinance as yf


from backtest_service.strategies import SmaCrossOver, SMA_RSI, SMA, Test_Strategy, MACDCrossoverStrategy, BollingerBandsStrategy, RSID_SMA, TurtleStrategy, MeanReversionStrategy

strategy_map = {
    "SMACrossOver": SmaCrossOver,

    "SMA_RSI": SMA_RSI,
    # "RSID_SMA": RSID_SMA,
    "SMA": SMA,
    "MACDCrossover": MACDCrossoverStrategy,
    # "TurtleStrategy": TurtleStrategy,  # Placeholder for now
    "BollingerBands": BollingerBandsStrategy,
    "MeanReversion": MeanReversionStrategy,
}

# Get today's date as a string in the format YYYY-MM-DD
today_date_string = datetime.now().strftime("%Y-%m-%d")


def download_yfinance_data_chunked(asset, start_date, end_date, interval, chunk_size=25):
    all_data = pd.DataFrame()
    current_date = pd.to_datetime(start_date)
    cal = USFederalHolidayCalendar()

    max_days_allowed = {
        "1m": 7, 
        "2m": 7,
        "5m": 60,
        "15m": 60,
        "30m": 60,
        "60m": 730,  
        "90m": 60,  
        "1h": 730,   
    }.get(interval, 730)  # Default to 730 for other intervals (1d, 5d, etc.)

    while current_date < pd.to_datetime(end_date):
        days_remaining = (pd.to_datetime(end_date) - current_date).days
        chunk_size = min(chunk_size, max_days_allowed, days_remaining) 
        
        next_date = current_date + timedelta(days=chunk_size)

        # Handle weekends and holidays
        while next_date.weekday() > 4 or next_date in cal.holidays():
            next_date -= timedelta(days=1)

        # Ensure we're fetching valid business days
        current_date = current_date + BDay(0)
        next_date = next_date + BDay(0)

        try:
            chunk = yf.download(asset, start=current_date, end=next_date, interval=interval)
            if not chunk.empty:
                all_data = pd.concat([all_data, chunk])
        except yf.YFinanceError as e:
            print(f"Error downloading data for {asset}: {e}")

        current_date = next_date

    return all_data


# start_date = "2023-02-01"
# end_date = "2024-06-28"
# asset = "GOOGL"
# interval="5m"
# data = download_yfinance_data_chunked(asset,start_date,end_date, interval=interval)
# data.head()



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
        strategy_name: str = "SMACrossOver",
        strategy_params={},
        interval:str="1d",
        start_date:str="2020-01-23",
        end_date:str=today_date_string,
        cash:int=100000,
        commission:float=0
  )->dict:
    print()
    # Map the strategy name to the actual strategy class

    strategy = strategy_map.get(strategy_name, SmaCrossOver)

    cerebro = prepare_cerebro(asset,strategy,interval,start_date,end_date,cash,commission, **strategy_params)
    result = run_test(cerebro)
    return result

def prepare_cerebro(asset,strategy,interval,start_date:str,end_date:str=datetime.now(),cash:int=100000,commission:float=0,  **strategy_params)->bt.Cerebro:
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


    data = yf.download(asset,start_date,end=end_date, interval='1d')
    # data = download_yfinance_data_chunked(asset,start_date,end_date,interval)

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

def run_test(cerebro: bt.Cerebro):
    result = {}

    cerebro.addanalyzer(SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(Returns, _name='returns')
    cerebro.addanalyzer(DrawDown, _name='draw')
    cerebro.addanalyzer(TradeAnalyzer, _name='trade')

    starting = cerebro.broker.getvalue()
    res = cerebro.run()
    final = cerebro.broker.getvalue()

    thestrat = res[0]

    sharpe = thestrat.analyzers.sharpe.get_analysis()
    return_val = thestrat.analyzers.returns.get_analysis()
    drawdown = thestrat.analyzers.draw.get_analysis()
    trade = thestrat.analyzers.trade.get_analysis()

    result["sharpe_ratio"] = sharpe['sharperatio']
    result["return"] = return_val['rtot']
    result['max_drawdown'] = drawdown['max']['drawdown']
    result['win_trade'] = trade.get('won', {}).get('total', 0)
    result['loss_trade'] = trade.get('lost', {}).get('total', 0)
    
    # Calculate total closed trades explicitly
    result['total_trade'] = result['win_trade'] + result['loss_trade'] 

    result['start_portfolio'] = starting
    result['final_portfolio'] = final

    return result