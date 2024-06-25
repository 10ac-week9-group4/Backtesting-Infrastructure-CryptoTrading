import logging
import os
from dotenv import load_dotenv
from confluent_kafka.admin import AdminClient, NewTopic

# Load environment variables
load_dotenv()
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094")
TOPIC_NAMES = os.getenv("TOPIC_NAMES", "")
PARTITIONS = int(os.getenv("PARTITIONS", "1"))
REPLICATION_FACTOR = int(os.getenv("REPLICATION_FACTOR", "1"))

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

def create_topics(topics, num_partitions, replication_factor, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS):
    """Creates Kafka topics if they don't exist."""
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})

    new_topics = [NewTopic(topic, num_partitions=num_partitions, replication_factor=replication_factor) for topic in topics]
    fs = admin_client.create_topics(new_topics, operation_timeout=10)  # Add timeout

    # Wait for each operation to finish.
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            logger.info(f"Topic '{topic}' created (or already exists)")
        except Exception as e:
            logger.error(f"Failed to create topic '{topic}': {e}")

if __name__ == "__main__":
    topics = [topic.strip() for topic in TOPIC_NAMES.split(",")] if TOPIC_NAMES else []
    if topics:
        create_topics(topics, PARTITIONS, REPLICATION_FACTOR)
    else:
        logger.error("No topics specified in TOPIC_NAMES environment variable.")