import os
import json
import time
import sys
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC")

producer = None


def initialize_producer():
    global producer

    retry_count = 0
    max_retries = 10
    retry_delay_seconds = 5

    while retry_count < max_retries:
        try:
            print("Attempting to connect to Kafka...")
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            print("Successfully connected to Kafka!")
            return
        except NoBrokersAvailable:
            retry_count += 1
            print(
                f"Kafka not available. Retrying in {retry_delay_seconds}s... (Attempt {retry_count}/{max_retries})"
            )
            time.sleep(retry_delay_seconds)

    print("Could not connect to Kafka after multiple retries. Exiting.")
    sys.exit(1)


def send_to_kafka(data: dict):
    if producer is None:
        print("Producer not initialized. Cannot send message.")
        return

    try:
        producer.send(KAFKA_TOPIC, value=data)
        producer.flush()
        print(f"Sent to Kafka: {data}")
    except Exception as e:
        print(f"Error sending to Kafka: {e}")
