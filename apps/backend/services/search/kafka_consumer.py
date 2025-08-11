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

def flatten_rfq_event(event_data: dict) -> dict:
    """Creates a flattened document for an RFQ to be indexed in ES."""
    return {
        "type": "rfq",
        "rfq_id": event_data.get("id"),
        "status": event_data.get("status"),
        "origin": event_data.get("segments", [{}])[0].get("origin_address"),
        "destination": event_data.get("segments", [{}])[0].get("destination_address"),
        "description": event_data.get("cargo", {}).get("description"),
        "created_at": event_data.get("created_at"),
    }

def flatten_order_event(event_data: dict) -> dict:
    """Creates a flattened document for an Order to be indexed in ES."""
    return {
        "type": "order",
        "order_id": event_data.get("orderId"),
        "client_id": event_data.get("clientId"),
        "supplier_id": event_data.get("supplierId"),
        "status": "created", # Initial status
        "price": event_data.get("totalPrice"),
        "currency": event_data.get("currency"),
        "created_at": event_data.get("confirmedAt"), # Or a more appropriate timestamp
    }

async def process_event(topic: str, event_data: dict):
    """
    Processes a single event by flattening it and calling the indexing service.
    """
    print(f"Search service received event from topic {topic}: {event_data}")
    try:
        doc_id = None
        doc_body = None
        index_name = None

        if topic == "rfq_created":
            doc_id = event_data.get("id")
            doc_body = flatten_rfq_event(event_data)
            index_name = service.RFQ_INDEX
        elif topic == "order_created":
            doc_id = event_data.get("orderId")
            doc_body = flatten_order_event(event_data)
            index_name = service.ORDER_INDEX

        if doc_id and doc_body and index_name:
            service.index_document(
                index_name=index_name,
                document_id=doc_id,
                document_body=doc_body
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
