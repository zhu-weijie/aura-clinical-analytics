import uuid
import random
from datetime import datetime

PATIENT_IDS = [str(uuid.uuid4()) for _ in range(5)]


def generate_clinical_data() -> dict:
    patient_id = random.choice(PATIENT_IDS)

    heart_rate = random.randint(55, 105)
    systolic_bp = random.randint(110, 140)
    diastolic_bp = random.randint(70, 90)
    spo2 = random.uniform(0.95, 0.99)

    return {
        "patient_id": patient_id,
        "timestamp": datetime.now().isoformat(),
        "heart_rate": heart_rate,
        "blood_pressure": f"{systolic_bp}/{diastolic_bp}",
        "spo2": round(spo2, 3),
    }
