from datetime import datetime
from database_models import Fact_Backtests, init_db
from backtest_service.backtesting import prepare_and_run_backtest
import mlflow
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

mlflow.set_tracking_uri(DATABASE_URL)

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
  with mlflow.start_run():
    if session is None:
      session = init_db()

    # Log parameters
    mlflow.log_params({
      "asset": scene["asset"],
      "strategy_name": scene["strategy"],
      "start_date": scene["start_date"],
      "end_date": scene["end_date"],
      "cash": scene["cash"],
      "commission": scene["commission"]
    })

    existing_results = get_existing_backtest_result(scene_id, session)
  
    if existing_results:
      print("EXISTING RESULTS: ", existing_results)
      results_with_id = existing_results.copy()
      results_with_id['SceneID'] = scene_id
    else:
      print("Running backtest...")
      backtest_results = prepare_and_run_backtest(
        asset=scene["asset"],
        strategy_name=scene["strategy"],
        start_date=scene["start_date"],
        end_date=scene["end_date"],
        cash=float(scene["cash"]),
        commission=float(scene["commission"]),
        strategy_params=scene["parameters"]
      )
      print("BACKTEST RESULTS: ", backtest_results)
      results_with_id = backtest_results.copy()
      results_with_id['SceneID'] = scene_id

      # Log metrics
      mlflow.log_metrics({
        "max_drawdown": backtest_results['max_drawdown'],
        "sharpe_ratio": backtest_results['sharpe_ratio'],
        "return": backtest_results['return']
      })

      # Optional: Log artifacts (e.g., plots)
      # mlflow.log_artifact("path/to/plot.png")

    return results_with_id

def save_single_backtest_result(scene_id, backtest_result, session=None):
  if session is None:
    session = init_db()
  
  existing_result = session.query(Fact_Backtests).filter_by(SceneID=scene_id).first()

  if existing_result:
    return # Do not save the result if it already exists
  
  if backtest_result['win_trade'] == 'Undefined':
    backtest_result['win_trade'] = None  # Convert to None, which will be inserted as NULL in the database

  if backtest_result['loss_trade'] == 'Undefined':
      backtest_result['loss_trade'] = None  # Convert to None, which will be inserted as NULL in the database

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
