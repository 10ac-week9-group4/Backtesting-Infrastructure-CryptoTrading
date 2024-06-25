import asyncio
import json
import os
from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv
import websockets

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094")
DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "ws://database-service:8001")

endpoint_mapping = {
  "stock_data": f"{DATABASE_SERVICE_URL}/ws/stock_data",
  "user_registrations": f"{DATABASE_SERVICE_URL}/ws/user_registrations",
  "backtest_results": f"{DATABASE_SERVICE_URL}/ws/backtest_results"
}

def create_kafka_consumer(topic_name, kafka_bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, group_id_suffix='consumer'):
  group_id = f"{topic_name}_{group_id_suffix}"
  conf = {
    'bootstrap.servers': kafka_bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest'
  }
  consumer = Consumer(conf)
  consumer.subscribe([topic_name])
  return consumer

async def consume_messages(consumer):
  while True:
    msg = consumer.poll(1.0)
    if msg is None:
      await asyncio.sleep(1)  # Sleep if no message is available
      continue
    if msg.error():
      if msg.error().code() == KafkaError._PARTITION_EOF:
        continue
      else:
        print(f"Error while consuming message: {msg.error()}")
        continue
    yield json.loads(msg.value().decode('utf-8'))

# Assuming endpoint_mapping and other necessary imports and variables are defined above

async def forward_message_to_service(topic, message, max_retries=5, retry_delay=2):
  endpoint = endpoint_mapping.get(topic)
  if not endpoint:
    print(f"No endpoint defined for topic: {topic}")
    return

  attempt = 0
  while attempt < max_retries:
    try:
      message_json = json.dumps(message)
      async with websockets.connect(endpoint) as ws:
        await ws.send(message_json)
      print(f"Successfully forwarded message to {endpoint}")
      return  # Exit function after successful sending
    except Exception as e:
      print(f"Attempt {attempt + 1}: Failed to forward message to {endpoint}, Error: {e}")
      attempt += 1
      await asyncio.sleep(retry_delay)  # Wait before retrying

  print(f"Failed to forward message to {endpoint} after {max_retries} attempts.")

async def consume_and_forward_messages(topic_names):
  async def consume_and_forward_for_topic(topic_name):
    consumer = create_kafka_consumer(topic_name)
    async for message in consume_messages(consumer):
      await forward_message_to_service(topic_name, message)
  tasks = [consume_and_forward_for_topic(topic_name) for topic_name in topic_names]
  await asyncio.gather(*tasks)

async def main():
  topic_names = ['stock_data', 'user_registrations', 'backtest_results']
  await consume_and_forward_messages(topic_names)

if __name__ == "__main__":
  print("Consumer service is running...")
  asyncio.run(main())