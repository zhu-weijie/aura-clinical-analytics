# packages/aura_core/src/aura_core/model/predictor.py
import joblib
import pandas as pd
import os

# --- Model Loading ---
# Construct the path to the model file
# The model file will be placed in the same directory as this script in the Docker container
MODEL_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "aura_risk_model.joblib")

# Load the model once when the module is imported
try:
    model = joblib.load(MODEL_PATH)
    print("Successfully loaded ML model from", MODEL_PATH)
except FileNotFoundError:
    print(
        f"Error: Model file not found at {MODEL_PATH}. Make sure it's copied into the Docker image."
    )
    model = None


def predict_patient_risk(clinical_data: dict) -> dict:
    """
    Predicts patient risk using the loaded scikit-learn model.
    """
    if model is None:
        return {"error": "Model not loaded"}

    try:
        # Prepare data for the model (must match training format)
        input_df = pd.DataFrame(
            [
                {
                    "heart_rate": clinical_data.get("heart_rate", 75),
                    "spo2": clinical_data.get("spo2", 0.98),
                }
            ]
        )

        # Make prediction
        prediction = model.predict(input_df)[0]
        prediction_proba = model.predict_proba(input_df)[0]

        risk_level = "high" if prediction == 1 else "low"
        score = float(prediction_proba[prediction])

        return {
            "patient_id": clinical_data.get("patient_id"),
            "risk_level": risk_level,
            "score": round(score, 3),
        }
    except Exception as e:
        return {"error": str(e)}
