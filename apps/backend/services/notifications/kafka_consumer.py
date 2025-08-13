import json
import os
import asyncio
import logging
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
# Subscribe to all topics that might generate a notification
TOPICS = [
    "order_status_updated",
    "review_created",
    "offer_accepted",
    "dispute_opened", # Assuming this event will exist
    "dispute_resolved" # Assuming this event will exist
]

from .email_sender import email_client

# --- Notification Routing ---
# Maps a topic to a template file and a subject line
EVENT_CONFIG = {
    "order_status_updated": {
        "template": "order_status_updated.html",
        "subject": "Your order {orderId:.8} has been updated!"
    },
    "review_created": {
        "template": "review_created.html",
        "subject": "You've received a new review!"
    },
    "offer_accepted": {
        "template": "offer_accepted.html",
        "subject": "Your offer for RFQ {rfq_id:.8} was accepted!"
    }
}

def process_event(topic: str, event_data: dict):
    """
    Processes an event by looking up its config, rendering the template,
    and calling the email client.
    """
    logging.info(f"Processing event from topic: {topic}")

    config = EVENT_CONFIG.get(topic)
    if not config:
        logging.warning(f"No config found for topic: {topic}")
        return

    # TODO: Implement a real mechanism to look up user/org emails from their IDs.
    recipient = "placeholder@example.com"

    try:
        subject = config["subject"].format(**event_data)
        html_body = email_client.render_template(config["template"], event_data)
        email_client.send_email(to=recipient, subject=subject, html_body=html_body)
    except KeyError as e:
        logging.error(f"Missing key {e} in event data for template {topic}: {event_data}")
    except Exception as e:
        logging.error(f"Failed to process event for topic {topic}: {e}", exc_info=True)


def start_consumer():
    """
    The main consumer loop.
    """
    logging.info("Notification service consumer started...")

    # Filter out topics that might not exist yet to avoid consumer errors
    # In a real app, topics should be created by a provisioning script.
    # For now, this is a placeholder for topics I know exist.
    available_topics = ["order_status_updated", "review_created", "offer_accepted"]

    consumer = KafkaConsumer(
        *available_topics,
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        auto_offset_reset='earliest',
        group_id='notifications-service-group',
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

    for message in consumer:
        process_event(message.topic, message.value)
