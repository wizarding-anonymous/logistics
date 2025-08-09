import json
import os
import asyncio
from kafka import KafkaConsumer
from dotenv import load_dotenv

from .database import AsyncSessionLocal
from . import service, schemas

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
OFFER_ACCEPTED_TOPIC = "offer_accepted"

consumer = KafkaConsumer(
    OFFER_ACCEPTED_TOPIC,
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
    auto_offset_reset='earliest', # Start reading at the earliest message
    group_id='orders-service-group', # Consumer group ID
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

async def process_offer_accepted_event(event_data: dict):
    """
    Processes a single OfferAccepted event.
    """
    print(f"Received event: {event_data}")
    try:
        # This is a simplified version. In a real app, you'd have more robust
        # data validation, perhaps using Pydantic schemas.
        order_data = schemas.OrderCreate(
            client_id=event_data["client_organization_id"],
            supplier_id=event_data["supplier_organization_id"],
            price_amount=event_data["price_amount"],
            price_currency=event_data["price_currency"],
        )

        # Get a new database session
        async with AsyncSessionLocal() as db:
            await service.create_order(db=db, order=order_data)
            print(f"Successfully created order from offer {event_data['offer_id']}")

    except Exception as e:
        # Basic error handling
        print(f"Error processing event {event_data}: {e}")


async def consume_events():
    """
    The main consumer loop.
    """
    print("Order service consumer started...")
    loop = asyncio.get_event_loop()
    for message in consumer:
        await loop.create_task(process_offer_accepted_event(message.value))
