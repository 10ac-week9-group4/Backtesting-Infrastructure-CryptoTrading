from confluent_kafka import Consumer, KafkaError
import json
import os
from dotenv import load_dotenv
import logging

import coloredlogs

coloredlogs.install()  # install a handler on the root logger

load_dotenv()
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094")


# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def create_kafka_consumer(topic_name, kafka_bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, group_id_suffix='consumer'):
    """Creates and configures a Kafka Consumer with topic-specific group ID."""
    group_id = f"{topic_name}_{group_id_suffix}"  
    conf = {
        'bootstrap.servers': kafka_bootstrap_servers,
        'group.id': group_id,
        'auto.offset.reset': 'earliest'  
    }
    consumer = Consumer(conf)
    consumer.subscribe([topic_name])
    return consumer

def consume_messages(consumer):
    """Consumes messages from the Kafka topic and yields deserialized messages."""
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue  # No message available within timeout

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                continue
            else:
                print(f"Error while consuming message: {msg.error()}")
                continue  # Continue to next message

        yield json.loads(msg.value().decode('utf-8'))  # Deserialize the message


def create_and_consume_messages(
    topic_name, 
    kafka_bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, 
    group_id_suffix='consumer', 
    timeout=1.0, 
):
    """Creates a consumer and asynchronously yields messages from the specified Kafka topic."""

    # Consumer configuration (same as before)
    group_id = f"{topic_name}_{group_id_suffix}"
    conf = {
        'bootstrap.servers': kafka_bootstrap_servers,
        'group.id': group_id,
        'auto.offset.reset': 'earliest',
    }

    consumer = Consumer(conf)
    consumer.subscribe([topic_name])

    try:
        while True:
            msg = consumer.poll(timeout)

            if msg is None:
                continue  # No message within timeout

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    logger.error(f"Error while consuming message: {msg.error()}")
                    continue

            message_value = json.loads(msg.value().decode('utf-8'))
            yield message_value  
    except KeyboardInterrupt:
        pass
    finally:
        consumer.close()
