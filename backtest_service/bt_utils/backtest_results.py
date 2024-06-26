from datetime import datetime
from database_models import Fact_Backtests, init_db
from backtest_service.backtesting import prepare_and_run_backtest

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

def save_single_backtest_result(scene_id, backtest_result, session=None):
  if session is None:
    session = init_db()
  
  existing_result = session.query(Fact_Backtests).filter_by(SceneID=scene_id).first()

  if existing_result:
    return # Do not save the result if it already exists
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
