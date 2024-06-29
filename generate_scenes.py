import json
from itertools import product

from src.shared import send_message_to_kafka, producer

# Function to generate parameter ranges based on a given criteria
def generate_param_ranges(start, end, intervals):
  ranges = []
  for interval in intervals:
    ranges.extend(range(start, end + 1, interval))
  return sorted(set(ranges))

# Modified generate_scenes function to use dynamic parameter ranges
def generate_scenes(strategy):
  symbol = strategy["symbol"]
  start_date = strategy["start_date"]
  cash = strategy["cash"]
  commission = strategy["commission"]
  end_date = strategy["end_date"]
  strategy_name = strategy["strategy"]
  param_ranges = strategy["indicator_params_range"]
  
  # Generate dynamic ranges for each parameter
  dynamic_ranges = {}
  for param, (start, end) in param_ranges.items():
    # Define intervals: start with 10, then 5, etc.
    intervals = [10, 5, 3, 2, 1]  # You can adjust this based on your needs
    dynamic_ranges[param] = generate_param_ranges(start, end, intervals)
  
  # Generate all combinations of parameters with dynamic ranges
  keys, values = zip(*dynamic_ranges.items())
  for v in product(*values):
    parameters = dict(zip(keys, v))
    yield {
      "symbol": symbol,
      "cash": cash,
      "commission": commission,
      "start_date": start_date,
      "end_date": end_date,
      "strategy": strategy_name,
      "parameters": parameters
    }
# Function to send scenes to Kafka
def send_scenes_to_kafka(scenes):
  for scene in scenes:
    send_message_to_kafka("scenes_topic", scene, flush=False)
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