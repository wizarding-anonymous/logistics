import json
import os
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
POD_CONFIRMED_TOPIC = "order_pod_confirmed"

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_pod_confirmed(order_details: dict):
    """
    Publishes an 'OrderPodConfirmed' event to Kafka.
    """
    try:
        producer.send(POD_CONFIRMED_TOPIC, value=order_details)
        producer.flush()
        print(f"Published event to {POD_CONFIRMED_TOPIC}: {order_details}")
    except Exception as e:
        print(f"Error publishing to Kafka: {e}")
