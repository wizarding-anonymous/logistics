import json
import os
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
OFFER_ACCEPTED_TOPIC = "offer_accepted"

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_offer_accepted(offer_details: dict):
    """
    Publishes an 'OfferAccepted' event to Kafka.

    The payload should contain all info needed for the orders service
    to create a new order.
    """
    try:
        producer.send(OFFER_ACCEPTED_TOPIC, value=offer_details)
        producer.flush() # Ensure the message is sent
        print(f"Published event to {OFFER_ACCEPTED_TOPIC}: {offer_details}")
    except Exception as e:
        # In a real app, handle this with more robust logging/retry logic
        print(f"Error publishing to Kafka: {e}")
