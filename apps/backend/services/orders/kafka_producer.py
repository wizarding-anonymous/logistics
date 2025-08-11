import json
import os
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
ORDER_COMPLETED_TOPIC = "order_completed"

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_order_completed(order_details: dict):
    """
    Publishes an 'OrderCompleted' event to Kafka, triggering billing.
    """
    try:
        producer.send(ORDER_COMPLETED_TOPIC, value=order_details)
        producer.flush()
        print(f"Published event to {ORDER_COMPLETED_TOPIC}: {order_details}")
    except Exception as e:
        print(f"Error publishing to Kafka: {e}")
