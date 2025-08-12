import json
import os
import asyncio
from kafka import KafkaConsumer
from dotenv import load_dotenv

from .database import AsyncSessionLocal
from . import service

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
ORDER_COMPLETED_TOPIC = "order_completed"

consumer = KafkaConsumer(
    ORDER_COMPLETED_TOPIC,
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
    auto_offset_reset='earliest',
    group_id='payments-service-group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

async def process_order_completed_event(event_data: dict):
    """
    Processes an OrderCompleted event to generate an invoice.
    """
    print(f"Payments service received event: {event_data}")
    try:
        # TODO: Add validation with Pydantic schemas
        async with AsyncSessionLocal() as db:
            await service.create_invoice_for_order(db=db, order_details=event_data)
            print(f"Successfully created invoice for order {event_data.get('orderId')}")
    except Exception as e:
        print(f"Error processing order completed event {event_data}: {e}")

async def consume_events():
    """
    Main consumer loop.
    """
    print("Payments service consumer started...")
    loop = asyncio.get_event_loop()
    for message in consumer:
        await loop.create_task(process_order_completed_event(message.value))
