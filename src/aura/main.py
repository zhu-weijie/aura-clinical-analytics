import time
from aura.simulation.simulator import generate_clinical_data


def run_app():
    print("AURA: Starting real-time clinical data simulation...")

    try:
        while True:
            data_record = generate_clinical_data()
            print(data_record)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nSimulation stopped.")


if __name__ == "__main__":
    run_app()
