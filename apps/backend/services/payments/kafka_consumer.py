import json
import os
import asyncio
from kafka import KafkaConsumer
from dotenv import load_dotenv

from .database import AsyncSessionLocal
from . import service

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
POD_CONFIRMED_TOPIC = "order_pod_confirmed"

consumer = KafkaConsumer(
    POD_CONFIRMED_TOPIC,
    bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
    auto_offset_reset='earliest',
    group_id='payments-service-group',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

async def process_event(event_data: dict):
    """
    Processes a single event by calling the appropriate service function.
    """
    print(f"Payments service received event: {event_data}")
    try:
        async with AsyncSessionLocal() as db:
            await service.process_payment_for_order(db=db, order_details=event_data)
            print(f"Successfully processed payment for order {event_data['order_id']}")
    except Exception as e:
        print(f"Error processing payment event {event_data}: {e}")

async def consume_events():
    """
    Main consumer loop.
    """
    print("Payments service consumer started...")
    loop = asyncio.get_event_loop()
    for message in consumer:
        # Create a new task for each message to allow concurrent processing if needed
        # In this simple case, it just runs the async function in the event loop
        await loop.create_task(process_event(message.value))
