import json
import backtrader as bt
from kafka import KafkaConsumer
from kafka import KafkaProducer

consumer = KafkaConsumer(
    'backtest_scenes',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)


def run_backtest(scene):
    # Fetch historical data (replace with your actual data fetching logic)
    data = 

    # Create cerebro instance
    cerebro = bt.Cerebro()

    # Add data feed
    cerebro.adddata(data)

    # Get strategy class from scene and add it to cerebro
    strategy_class = globals()[scene['strategy']]  # Assuming strategy classes are defined globally
    cerebro.addstrategy(strategy_class, **scene['parameters'])

    # Run the backtest
    cerebro.run()

    # Extract results (replace with your actual result extraction logic)
    result = {
        'final_value': cerebro.broker.getvalue(),
        'sharpe_ratio': ...,
        # ... other metrics
    }

    return result

producer = KafkaProducer(bootstrap_servers='localhost:9092')  # Replace with your Kafka broker address
for message in consumer:
    scene = message.value
    # Execute backtest (replace with your actual backtesting logic)
    result = run_backtest(scene)

    producer.send("backtest_results", result.encode())

