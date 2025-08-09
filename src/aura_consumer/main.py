import os
import json
import sys
import time
import logging
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
import requests

KAFKA_BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC")
PREDICTION_API_URL = os.environ.get("PREDICTION_API_URL")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)


def wait_for_api():
    logging.info(
        f"Consumer: Waiting for API service to be ready at {PREDICTION_API_URL.replace('/predict', '')}..."
    )
    retry_count = 0
    max_retries = 15
    retry_delay_seconds = 3
    api_root_url = PREDICTION_API_URL.replace("/predict", "")

    while retry_count < max_retries:
        try:
            response = requests.get(api_root_url)
            if response.status_code == 200:
                logging.info("Consumer: API service is ready!")
                return
        except requests.exceptions.ConnectionError:
            pass

        retry_count += 1
        logging.warning(
            f"Consumer: API not ready. Retrying... ({retry_count}/{max_retries})"
        )
        time.sleep(retry_delay_seconds)

    logging.critical("Consumer: Could not connect to API service. Exiting.")
    sys.exit(1)


def create_consumer():
    retry_count = 0
    max_retries = 10
    retry_delay_seconds = 5

    while retry_count < max_retries:
        try:
            logging.info("Consumer: Attempting to connect to Kafka...")
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                auto_offset_reset="earliest",
                group_id="aura-risk-assessors",
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            )
            logging.info("Consumer: Successfully connected to Kafka!")
            return consumer
        except NoBrokersAvailable:
            retry_count += 1
            logging.warning(
                f"Consumer: Kafka not available. Retrying... ({retry_count}/{max_retries})"
            )
            time.sleep(retry_delay_seconds)

    logging.critical(
        "Consumer: Could not connect to Kafka after multiple retries. Exiting."
    )
    sys.exit(1)


def process_messages(consumer):
    logging.info("Consumer: Starting to listen for messages...")
    for message in consumer:
        clinical_data = message.value
        try:
            response = requests.post(PREDICTION_API_URL, json=clinical_data)
            response.raise_for_status()
            prediction = response.json()

            if prediction.get("risk_level") == "high":
                logging.critical(
                    f"HIGH_RISK_ALERT - Patient: {prediction.get('patient_id')}, Score: {prediction.get('score')}"
                )
            else:
                logging.info(
                    f"Prediction Received - Patient: {prediction.get('patient_id')}, Risk: {prediction.get('risk_level')}, Score: {prediction.get('score')}"
                )

        except requests.exceptions.RequestException as e:
            logging.error(f"Consumer: Could not call prediction API. Error: {e}")
        except Exception as e:
            logging.error(f"Consumer: An unexpected error occurred: {e}")


if __name__ == "__main__":
    wait_for_api()

    kafka_consumer = create_consumer()
    process_messages(kafka_consumer)
