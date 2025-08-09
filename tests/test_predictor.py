from aura_core.model.predictor import predict_patient_risk


def test_predict_high_risk():
    high_risk_data = {"heart_rate": 105, "spo2": 0.95}
    prediction = predict_patient_risk(high_risk_data)
    assert prediction["risk_level"] == "high"
    assert prediction["score"] > 0.5


def test_predict_low_risk():
    low_risk_data = {"heart_rate": 70, "spo2": 0.98}
    prediction = predict_patient_risk(low_risk_data)
    assert prediction["risk_level"] == "low"
    assert prediction["score"] > 0.5


def test_predict_missing_data():
    missing_data = {"heart_rate": 80}
    prediction = predict_patient_risk(missing_data)
    assert prediction["risk_level"] == "low"
    assert prediction["score"] > 0.5
