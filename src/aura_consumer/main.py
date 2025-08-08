import os
import json
import sys
import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import requests

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC")
PREDICTION_API_URL = os.environ.get("PREDICTION_API_URL")


def create_consumer():
    retry_count = 0
    max_retries = 10
    retry_delay_seconds = 5

    while retry_count < max_retries:
        try:
            print("Consumer: Attempting to connect to Kafka...")
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset="earliest",  # Start reading at the earliest message
                group_id="aura-risk-assessors",  # Consumer group ID
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            )
            print("Consumer: Successfully connected to Kafka!")
            return consumer
        except NoBrokersAvailable:
            retry_count += 1
            print(
                f"Consumer: Kafka not available. Retrying... ({retry_count}/{max_retries})"
            )
            time.sleep(retry_delay_seconds)

    print("Consumer: Could not connect to Kafka after multiple retries. Exiting.")
    sys.exit(1)


def process_messages(consumer):
    print("Consumer: Starting to listen for messages...")
    for message in consumer:
        clinical_data = message.value
        try:
            # Call the prediction API
            response = requests.post(PREDICTION_API_URL, json=clinical_data)
            response.raise_for_status()  # Raise an exception for bad status codes
            prediction = response.json()

            print(f"Prediction Received: {prediction}")

        except requests.exceptions.RequestException as e:
            print(f"Consumer: Could not call prediction API. Error: {e}")
        except Exception as e:
            print(f"Consumer: An unexpected error occurred: {e}")


if __name__ == "__main__":
    kafka_consumer = create_consumer()
    process_messages(kafka_consumer)
