import hashlib
import json
import os

from database_models import init_db, Dim_Strategy, Fact_Backtests, Dim_Scene, Dim_Date
from datetime import datetime

os.chdir("../../../")
from src.backtesting.run_backtest import prepare_and_run_backtest, prepare_and_run_many_backtests




from itertools import product


session = init_db()  # Assuming session is not global, reinitialize


def generate_param_combinations(param_ranges):
    # Extract parameter names and their corresponding ranges
    param_names = list(param_ranges.keys())
    param_values = [param_ranges[name] for name in param_names]
    
    # Generate all combinations of parameter values
    all_combinations = product(*param_values)
    
    # Convert each combination of values back into a dictionary with the correct parameter names
    combination_dicts = [{param_names[i]: combo[i] for i in range(len(param_names))} for combo in all_combinations]
    
    return combination_dicts


def generate_strategy_id(strategy_params, asset, start_date, end_date):
    id_components = {
        'strategy_params': strategy_params,
        'asset': asset,
        'start_date': start_date,
        'end_date': end_date
    }
    serialized_components = json.dumps(id_components, sort_keys=True)
    strategy_id = hashlib.sha256(serialized_components.encode()).hexdigest()
    return strategy_id

def run_many_backtests(asset, indicator_params_range, start_date, cash, commission):
    combinations = generate_param_combinations(indicator_params_range)
    all_results = []
    for combination in combinations:
        # Generate a unique strategyID for each set of parameters
        strategy_id = generate_strategy_id(combination, asset, start_date, strategy['end_date'])
        
        # Here, you would run your backtest based on the strategy_params
        # For demonstration, let's assume the backtest returns a dictionary of results
        # Replace the following line with your actual backtest call

        # backtest_results = {"profit": 1000, "max_drawdown": 5}  # Example results
        backtest_results = prepare_and_run_backtest(strategy_params=combination)
        
        # Add the strategyID to the results
        results_with_id = backtest_results.copy()
        results_with_id['strategyID'] = strategy_id
        
        all_results.append(results_with_id)
    return all_results

# Your existing strategy setup
strategy = {
  "start_date": "2022-12-19",
  "end_date": "2023-02-19",
  "indicator": "SmaCrossOver",
  "indicator_params_range": {
    'pfast': [10, 15],
    'pslow': [30, 40]
  }
}




def save_strategy(strategy_params, asset, start_date, end_date):
  session = init_db()  # Initialize DB session
  # Create and save the strategy
  strategy = Dim_Strategy(
    StrategyName=strategy_params['indicator'],
    StrategyDescription=json.dumps(strategy_params),
    Indicator=strategy_params['indicator'],
    IndicatorParameterNames=json.dumps(list(strategy_params['indicator_params_range'].keys()))
  )
  session.add(strategy)
  session.commit()
  return strategy.StrategyID

# backtest_result_examples = {
#    'sharpe_ratio': -61.7130814514063, 
#    'return': 0.000609949259972471, 
#    'max_drawdown': 0.06566744297938924, 
#    'win_trade': 41, 
#    'loss_trade': 41, 
#    'total_trade': 83, 
#    'start_portfolio': 100000, 
#    'final_portfolio': 100061.01353168488, 
#    'strategyID': '835d26b638b3c1ad41e937244edcbb0e4c07a1751858a614d8ef7bfef3db14d9'
# }

from datetime import datetime


def save_single_backtest_result(strategy_id, backtest_result, session=None):
  if session is None:
    session = init_db()
  
  backtest = Fact_Backtests(
    StrategyID=strategy_id,
    MaxDrawdown=backtest_result['max_drawdown'],
    SharpeRatio=backtest_result['sharpe_ratio'],
    Return=backtest_result['return'],
    TradeCount=backtest_result['total_trade'],
    WinningTrades=backtest_result['win_trade'],
    LosingTrades=backtest_result['loss_trade'],
    StartPortfolio=backtest_result['start_portfolio'],
    FinalPortfolio=backtest_result['final_portfolio'],
    CreatedAt=datetime.now()  # Add the current time here

  )
  session.add(backtest)
  session.commit()

def save_backtest_results(strategy_id, backtest_results):
  session = init_db()  # Assuming session is not global, reinitialize
  for result in backtest_results:
    save_single_backtest_result(session, strategy_id, result)
  session.commit()



def save_scene(strategy_id, asset, start_date, end_date, parameters):
  session = init_db()
  scene = Dim_Scene(
    StrategyID=strategy_id,
    Symbol=asset,
    StartDate=start_date,
    EndDate=end_date,
    Parameters=json.dumps(parameters)
  )
  session.add(scene)
  session.commit()

# Example usage
# strategy_id = save_strategy(strategy_params=strategy, asset="GOOGL", start_date="2022-12-19", end_date="2023-02-19")
# backtest_results = run_many_backtests("GOOGL", indicator_params_range, "2022-12-19", 100000, 0)
# save_backtest_results(strategy_id, backtest_results)
# save_scene(strategy_id, "GOOGL", "2022-12-19", "2023-02-19", strategy_params)




def main(strategy):
  # Initialize DB session
  session = init_db()

  # Save the strategy and get its ID
  strategy_id = save_strategy(strategy_params=strategy, asset="GOOGL", start_date=strategy["start_date"], end_date=strategy["end_date"])
  
  # Run backtests for all combinations of parameters
  backtest_results = run_many_backtests(asset="GOOGL", indicator_params_range=strategy["indicator_params_range"], start_date=strategy["start_date"], cash=100000, commission=0.001)
  
  # Save each backtest result
  for result in backtest_results:
    save_single_backtest_result(strategy_id=strategy_id, backtest_result=result, session=session)
  
  # Save the scene
  save_scene(strategy_id=strategy_id, asset="GOOGL", start_date=strategy["start_date"], end_date=strategy["end_date"], parameters=strategy)

if __name__ == "__main__":
  strategy = {
    "start_date": "2022-12-19",
    "end_date": "2023-02-19",
    "indicator": "SmaCrossOver",
    "indicator_params_range": {
      'pfast': [10],
      'pslow': [30]
    }
  }
  main(strategy)


# indicator_params_range = strategy['indicator_params_range']
# strategy_params = strategy['indicator_params_range']

# # Running backtests with the modified function
# results = run_many_backtests(
#   asset="GOOGL",
#   indicator_params_range=indicator_params_range,
#   start_date=strategy["start_date"],
#   cash=100000,
#   commission=0
# )

# Example output
# print(results)


# Example usage with a dynamic set of parameters
# indicator_params_range = {
#     'pfast': [10, 15],
#     'pslow': [30, 40],
#     # Add more parameters as needed
#     # 'ema': [20, 25]
# }

# combinations = generate_param_combinations(indicator_params_range)
# for combo in combinations:
#     print(combo)