import time


from aura_core.simulation.simulator import generate_clinical_data
from aura.messaging.producer import initialize_producer, send_to_kafka


def run_app():
    initialize_producer()

    print("AURA: Starting data production...")

    try:
        while True:
            data_record = generate_clinical_data()
            send_to_kafka(data_record)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nProducer stopped.")


if __name__ == "__main__":
    run_app()
