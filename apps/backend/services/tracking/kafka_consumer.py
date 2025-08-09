import json
import logging
import asyncio
from kafka import KafkaConsumer
from sqlalchemy.orm import sessionmaker
from . import models, database

# Configure logger
log = logging.getLogger(__name__)

# Standalone session maker for the consumer
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=database.engine, class_=database.AsyncSession)

async def save_tracking_event(event_data: dict):
    """
    Saves a tracking event to the database.
    """
    async with SessionLocal() as db:
        new_event = models.TrackingEvent(
            order_id=event_data.get("orderId"),
            status=event_data.get("newStatus"),
            notes=event_data.get("notes"),
            timestamp=event_data.get("timestamp")
        )
        db.add(new_event)
        await db.commit()
        log.info(f"Saved tracking event for order {new_event.order_id}")

def consume_order_events():
    """
    Consumes events from the 'order_events' Kafka topic and processes them.
    This function runs in a synchronous manner and should be started in a separate thread or process.
    """
    consumer = KafkaConsumer(
        'order_events',
        bootstrap_servers=['kafka:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='tracking-service-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    log.info("Tracking service Kafka consumer started...")
    for message in consumer:
        event = message.value
        log.info(f"Received event: {event}")

        event_type = event.get("eventType")

        # We are interested in status updates to build the tracking history
        if event_type == "OrderStatusUpdated":
            payload = event.get("payload", {})
            # Add the event timestamp to the payload for storage
            payload['timestamp'] = event.get("timestamp")

            # Since this consumer loop is synchronous, we run the async DB operation
            # in a new event loop.
            try:
                asyncio.run(save_tracking_event(payload))
            except Exception as e:
                log.error(f"Error processing event: {e}", exc_info=True)
        elif event_type == "OrderCreated":
             payload = event.get("payload", {})
             payload['newStatus'] = "created"
             payload['notes'] = "Order has been created."
             payload['timestamp'] = event.get("timestamp")
             try:
                asyncio.run(save_tracking_event(payload))
             except Exception as e:
                log.error(f"Error processing event: {e}", exc_info=True)

if __name__ == "__main__":
    # This allows running the consumer as a standalone script for testing or deployment.
    logging.basicConfig(level=logging.INFO)
    consume_order_events()
