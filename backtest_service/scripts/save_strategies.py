import json
from database_models import init_db
import os
import sys
from dotenv import load_dotenv

# sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backtest_service.bt_utils.strategy_utils import save_strategy

load_dotenv()
DATABASE_URL = os.environ.get('DATABASE_URL')



"""
    1. Import necessary modules (json, sqlalchemy, strategy_utils)
    2. Define a function to load strategies from a JSON file:
      a. Open the JSON file.
      b. Load the content into a Python object (list of dictionaries).
    3. Define a main function:
      a. Create a database session.
      b. Call the function to load strategies.
      c. Iterate over each strategy in the loaded list.
      d. For each strategy, call save_strategy from strategy_utils with the strategy and session.
    4. If this script is run directly, call the main function.
"""

def load_strategies_from_json(file_path):
  with open(file_path, 'r') as file:
    strategies = json.load(file)
  return strategies

def main():
  session = init_db()
  strategies = load_strategies_from_json('backtest_service/strategies/strategies.json')
  for strategy_params in strategies:
    strategy_id = save_strategy(strategy_params)
    print(f"Strategy saved with ID: {strategy_id}")

if __name__ == "__main__":
  main()