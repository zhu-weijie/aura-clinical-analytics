def predict_patient_risk(clinical_data: dict) -> dict:
    heart_rate = clinical_data.get("heart_rate", 75)
    spo2 = clinical_data.get("spo2", 0.98)

    if heart_rate > 100 or spo2 < 0.96:
        risk_level = "high"
        score = 0.85
    elif heart_rate > 90 or spo2 < 0.97:
        risk_level = "medium"
        score = 0.6
    else:
        risk_level = "low"
        score = 0.2

    return {
        "patient_id": clinical_data.get("patient_id"),
        "risk_level": risk_level,
        "score": score,
    }
