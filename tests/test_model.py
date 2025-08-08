from src.aura.model.predictor import predict_patient_risk

low_risk_data = {"patient_id": "test-patient-1", "heart_rate": 80, "spo2": 0.98}

high_risk_data = {"patient_id": "test-patient-2", "heart_rate": 105, "spo2": 0.99}

print("--- Testing Model Logic ---")
low_risk_prediction = predict_patient_risk(low_risk_data)
high_risk_prediction = predict_patient_risk(high_risk_data)

print(f"Low risk input -> Prediction: {low_risk_prediction}")
print(f"High risk input -> Prediction: {high_risk_prediction}")
print("-------------------------")
