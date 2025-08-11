import json
import os
import asyncio
from kafka import KafkaConsumer
from dotenv import load_dotenv

from . import service

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPICS = ["rfq_created", "order_created"] # Add more topics as needed

consumer = KafkaConsumer(
    *TOPICS,
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
    auto_offset_reset='earliest',
    group_id='search-service-indexer-group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

async def process_event(topic: str, event_data: dict):
    """
    Processes a single event by calling the indexing service.
    """
    print(f"Search service received event from topic {topic}: {event_data}")
    try:
        if topic == "rfq_created":
            # Assuming the event data is the full RFQ object
            service.index_document(
                index_name=service.RFQ_INDEX,
                document_id=event_data['id'],
                document_body=event_data
            )
        elif topic == "order_created":
            service.index_document(
                index_name=service.ORDER_INDEX,
                document_id=event_data['orderId'],
                document_body=event_data
            )
    except Exception as e:
        print(f"Error indexing event {event_data}: {e}")

async def consume_events():
    """
    Main consumer loop.
    """
    print("Search service consumer started...")
    loop = asyncio.get_event_loop()
    for message in consumer:
        await loop.create_task(process_event(message.topic, message.value))
