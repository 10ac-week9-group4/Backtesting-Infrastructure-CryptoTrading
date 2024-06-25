import json
import socket
import logging
from confluent_kafka import Producer
import os
from dotenv import load_dotenv

load_dotenv()
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094")

logger = logging.getLogger(__name__)
# Set up logging
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Kafka Configuration
def create_kafka_producer(kafka_bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, extra_config=None):
    """Creates and configures a Kafka Producer."""
    conf = {
        'bootstrap.servers': kafka_bootstrap_servers,
        'client.id': socket.gethostname(),
        'acks': 'all',
        'retries': 3,
        'batch.size': 16384,
        'linger.ms': 100,
    }
    if extra_config:
        conf.update(extra_config)  # Allow overriding default config
    try:
        producer = Producer(conf)
        return producer, True
    except Exception as e:
        logger.error(f"Error creating Kafka producer: {e}")
        return None, False

# Create the Kafka Producer (once)
producer, success = create_kafka_producer()
if not success:
    # Handle the error (e.g., log an error message and exit the script)
    exit(1)

# Function to send messages
def send_message_to_kafka(topic_name, message, key=None):
    """Sends a JSON-serialized message to the specified Kafka topic."""
    try:
        producer.produce(topic_name, key=key, value=json.dumps(message).encode('utf-8'))
        producer.flush()  # Ensure message delivery
        logger.info(f"Message sent to Kafka topic '{topic_name}': {message}")
        return True
    except Exception as e:
        logger.error(f"Error producing message: {e}")
        return False