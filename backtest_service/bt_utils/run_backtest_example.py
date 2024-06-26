import hashlib
import json
import os

from database_models import init_db, Dim_Strategy, Fact_Backtests, Dim_Scene, Dim_Date
from datetime import datetime

# os.chdir("../../../")
# from src.backtesting.run_backtest import prepare_and_run_backtest, prepare_and_run_many_backtests




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



def save_strategy(strategy_params):
  session = init_db()  # Initialize DB session

  # Serialize strategy parameters to create a unique identifier
  serialized_params = json.dumps(strategy_params, sort_keys=True)
  strategy_identifier = hashlib.sha256(serialized_params.encode()).hexdigest()

  # Check if a strategy with this identifier already exists
  existing_strategy = session.query(Dim_Strategy).filter_by(StrategyIdentifier=strategy_identifier).first()

  if existing_strategy is None:
    # If it does not exist, create and save the new strategy
    strategy = Dim_Strategy(
      StrategyIdentifier=strategy_identifier,
      StrategyName=strategy_params['indicator'],
      StrategyDescription=json.dumps(strategy_params),
      Indicator=strategy_params['indicator'],
      IndicatorParameterNames=json.dumps(list(strategy_params['indicator_params_range'].keys()))
    )
    session.add(strategy)
    session.commit()
    return strategy.StrategyID  # Return the new StrategyID
  else:
    # If it exists, return the existing StrategyID
    return existing_strategy.StrategyID

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

def get_existing_backtest_result(scene_id, session=None):
  if session is None:
    session = init_db()

  # Query the database for existing backtest results using the Scene Id
  existing_result = session.query(Fact_Backtests).filter_by(SceneID=scene_id).first()
  if existing_result:
    # Convert the database model instance to a dictionary or a similar structure that matches the expected backtest result format
    return {
      'max_drawdown': existing_result.MaxDrawdown,
      'sharpe_ratio': existing_result.SharpeRatio,
      'return': existing_result.Return,
      'win_trade': existing_result.WinningTrades,
      'loss_trade': existing_result.LosingTrades,
      'total_trade': existing_result.TradeCount,
      'start_portfolio': existing_result.StartPortfolio,
      'final_portfolio': existing_result.FinalPortfolio,
      'scene_id': existing_result.SceneID,
      'created_at': existing_result.CreatedAt
    }
  else:
    return None

def generate_scene_key(strategy_params, asset, start_date, end_date):
    id_components = {
        'strategy_params': strategy_params,
        'asset': asset,
        'start_date': start_date,
        'end_date': end_date
    }
    serialized_components = json.dumps(id_components, sort_keys=True)
    strategy_id = hashlib.sha256(serialized_components.encode()).hexdigest()
    return strategy_id

# New function to handle a single backtest execution
def execute_single_backtest(scene, scene_id, session=None):
  if session is None:
    session = init_db()
  # Generate SceneID for the combination
  # scene_key = generate_scene_key(combination, asset, start_date, end_date)
  
  # Check if results for this SceneID already exist
  existing_results = get_existing_backtest_result(scene_id, session)
  if existing_results:
    results_with_id = existing_results.copy()
    results_with_id['SceneID'] = scene_id
  else:
    # If no existing results, run the backtest
    backtest_results = prepare_and_run_backtest(strategy_params=scene["parameters"])
    results_with_id = backtest_results.copy()
    results_with_id['SceneID'] = scene_id
    # Save the new backtest result here if needed
  
  return results_with_id

# Refactored run_many_backtests function
# def run_many_backtests(asset, indicator_params_range, start_date, cash, commission, session=None):
#   if session is None:
#     session = init_db()


#   combinations = generate_param_combinations(indicator_params_range)
#   all_results = []
#   for combination in combinations:
#     result = execute_single_backtest(asset, combination, start_date, cash, commission, session)
#     all_results.append(result)
#   return all_results


def save_single_backtest_result(scene_id, backtest_result, session=None):
  if session is None:
    session = init_db()
  
  backtest = Fact_Backtests(
    SceneID=scene_id,
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



def save_scene(scene, strategy_id):
  session = init_db()

  # Serialize parameters to generate a unique SceneKey
  serialized_params = json.dumps(scene, sort_keys=True)
  # Generate SceneKey using SHA256 hash
  scene_key = hashlib.sha256(serialized_params.encode()).hexdigest()

  # Check if a scene with the same SceneKey already exists
  existing_scene = session.query(Dim_Scene).filter_by(SceneKey=scene_key).first()

  if existing_scene is None:
    # If no existing scene, save the new scene
    scene = Dim_Scene(
      SceneKey=scene_key,
      StrategyID=strategy_id,
      Symbol=scene["asset"],
      Cash=scene["cash"],
      Commission=scene["commission"],
      StartDate=scene["start_date"],
      EndDate=scene["end_date"],
      Parameters=json.dumps(scene["parameters"])
    )
    session.add(scene)
    session.commit()
    return scene.SceneID  # Return the SceneID after saving the scene
  else:
    # If a scene with the same SceneKey exists, return its SceneID (or handle as needed)
    return existing_scene.SceneID



# Example usage
# strategy_id = save_strategy(strategy_params=strategy, asset="GOOGL", start_date="2022-12-19", end_date="2023-02-19")
# backtest_results = run_many_backtests("GOOGL", indicator_params_range, "2022-12-19", 100000, 0)
# save_backtest_results(strategy_id, backtest_results)
# save_scene(strategy_id, "GOOGL", "2022-12-19", "2023-02-19", strategy_params)




def main(strategy):
  # Initialize DB session
  session = init_db()

  asset = "GOOGL"
  start_date = strategy["start_date"]
  end_date = strategy["end_date"]
  cash = 105000
  commission = 0.000
  parameters = strategy
  indicator_params_range = strategy["indicator_params_range"]

  # Save the strategy and get its ID
  strategy_id = save_strategy(strategy_params=strategy)
  
  # Save the scene
  # scene_id = save_scene(strategy_id=strategy_id, asset="GOOGL", start_date=strategy["start_date"], parameters=strategy)

  # Run backtests for all combinations of parameters
  # backtest_results = run_many_backtests(asset="GOOGL", indicator_params_range=strategy["indicator_params_range"], start_date=strategy["start_date"], cash=100000, commission=0.001)


  params_combinations = generate_param_combinations(indicator_params_range)
  all_results = []
  for parameters in params_combinations:
    scene_details = {
      "asset": asset,
      "start_date": start_date,
      "end_date": end_date,
      "cash": cash,
      "commission": commission,
      "parameters": parameters
    }

    # save_scene or get scene_id if scene already exists
    scene_id = save_scene(scene_details, strategy_id)

    result = execute_single_backtest(scene_details, scene_id, session)
    save_single_backtest_result(scene_id, result, session)
    all_results.append(result)
  return all_results

  # Save each backtest result
  # for result in backtest_results:
    # save_single_backtest_result(scene_id=scene_id, backtest_result=result, session=session)
  

if __name__ == "__main__":
  strategy = {
    "start_date": "2022-12-19",
    "end_date": "2023-02-19",
    "cash": 100000,
    "commission": 0.001,
    "indicator": "SmaCrossOver",
    "indicator_params_range": {
      'pfast': [10, 40],
      'pslow': [30, 60]
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