from confluent_kafka import Producer
import yfinance as yf
import json
import time

# If you are running the Kafka broker locally, use the following URL
KAFKA_BROKER_URL = "localhost:9094"

# If you are running the Kafka broker in a Docker container, use the following URL
# KAFKA_BROKER_URL = "kafka:9092"

# Callback function to handle delivery reports
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def fetch_and_send_stock_data(symbol, period="1d", max_retries=2):
    # Fetch stock data
    stock = yf.Ticker(symbol)
    hist = stock.history(period=period)  # Fetch data for the specified period

    # Kafka configuration
    conf = {'bootstrap.servers': KAFKA_BROKER_URL}
    producer = Producer(**conf)
    topic = 'stock_data'

    # Iterate over each row in the DataFrame
    for index, row in hist.iterrows():
        # Prepare data for sending to Kafka
        data = row.to_dict()
        data['symbol'] = symbol  # Add the symbol to the data
        data['date'] = index.strftime('%Y-%m-%d')  # Add the date to the data

        # Attempt to send data to Kafka with retries
        for attempt in range(max_retries):
            try:
                print(str(data))
                producer.produce(topic, json.dumps(data).encode('utf-8'), callback=delivery_report)
                producer.flush()
                break  # Exit the retry loop on success
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    print("Max retries reached. Failed to send data to Kafka.")

# Example usage for a longer period, e.g., 5 days
# fetch_and_send_stock_data("AAPL", "5d")

# TODO - split the fetch_and_send_stock_data function into two separate functions