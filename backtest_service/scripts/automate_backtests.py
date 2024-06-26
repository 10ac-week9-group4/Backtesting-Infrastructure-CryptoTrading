import json
from itertools import product

from shared import send_message_to_kafka, producer

# Function to generate parameter combinations
def generate_scenes(strategy):
  symbol = strategy["symbol"]
  start_date = strategy["start_date"]
  cash = strategy["cash"]
  commission = strategy["commission"]
  end_date = strategy["end_date"]
  strategy = strategy["strategy"]
  param_ranges = strategy["indicator_params_range"]
  
  # Generate all combinations of parameters
  keys, values = zip(*param_ranges.items())
  for v in product(*values):
    parameters = dict(zip(keys, v))
    yield {
      "symbol": symbol,
      "cash": cash,
      "commission": commission,
      "start_date": start_date,
      "end_date": end_date,
      "strategy": strategy,
      "parameters": parameters
    }

# Function to send scenes to Kafka
def send_scenes_to_kafka(scenes):
  for scene in scenes:
    send_message_to_kafka("backtest_scenes", scene, flush=False)
  producer.flush()

# Main function to read JSON and process strategies
def process_strategies(file_path):
  with open(file_path) as f:
    strategies = json.load(f)

  for strategy in strategies:
    scenes = generate_scenes(strategy)
    send_scenes_to_kafka(scenes)

# Example usage
if __name__ == "__main__":
  process_strategies("strategy_combinations.json")