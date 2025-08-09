# packages/aura_core/src/aura_core/model/predictor.py
import joblib
import pandas as pd
import importlib.resources  # Use the modern, correct library for package data


# --- Model Loading using importlib.resources ---
def _load_model():
    """Loads the model using a reliable path within the package."""
    try:
        # 'files()' gets a traversable object for the specified package.
        # We specify the sub-package 'aura_core.model.assets'.
        # Then, we join the path to our model file.
        model_resource = importlib.resources.files("aura_core.model.assets").joinpath(
            "aura_risk_model.joblib"
        )

        # 'as_file()' is a context manager that provides a real filesystem path for the resource.
        with importlib.resources.as_file(model_resource) as model_path:
            print(f"Attempting to load ML model from filesystem path: {model_path}")
            model = joblib.load(model_path)
            print("Successfully loaded ML model.")
            return model

    except (FileNotFoundError, ModuleNotFoundError) as e:
        # This will now give us a much clearer error if the file is not found
        print(
            f"CRITICAL ERROR: Could not find or load model file via importlib.resources. Error: {e}"
        )
        return None


# Load the model once when this module is first imported.
model = _load_model()


def predict_patient_risk(clinical_data: dict) -> dict:
    """
    Predicts patient risk using the loaded scikit-learn model.
    """
    if model is None:
        return {"error": "Model not loaded. Check startup logs for errors."}

    try:
        # Prepare data for the model
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
