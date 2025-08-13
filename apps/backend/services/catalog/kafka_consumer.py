import json
import os
import asyncio
from kafka import KafkaConsumer
from dotenv import load_dotenv

from .database import AsyncSessionLocal
from . import service

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
REVIEW_CREATED_TOPIC = "review_created"

async def process_review_created_event(event_data: dict):
    """
    Processes a ReviewCreated event to update a supplier's service ratings.
    """
    print(f"Catalog service received event: {event_data}")
    try:
        supplier_id = event_data["supplier_id"]
        new_rating = event_data["rating"]

        async with AsyncSessionLocal() as db:
            await service.update_supplier_ratings(db=db, supplier_id=supplier_id, new_rating=new_rating)
            print(f"Successfully updated ratings for supplier {supplier_id}")

    except Exception as e:
        print(f"Error processing review created event {event_data}: {e}")

def start_consumer():
    """
    The main consumer loop.
    """
    print("Catalog service consumer started...")
    consumer = KafkaConsumer(
        REVIEW_CREATED_TOPIC,
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        auto_offset_reset='earliest',
        group_id='catalog-service-group',
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    loop = asyncio.get_event_loop()
    for message in consumer:
        loop.create_task(process_review_created_event(message.value))
