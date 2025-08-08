from fastapi import FastAPI
from pydantic import BaseModel, Field


from aura.model.predictor import predict_patient_risk

app = FastAPI(title="AURA Prediction API")


class ClinicalData(BaseModel):
    patient_id: str
    timestamp: str
    heart_rate: int
    blood_pressure: str
    spo2: float = Field(..., gt=0, lt=1)


@app.get("/")
def read_root():
    return {"message": "AURA Prediction API is running."}


@app.post("/predict")
def predict(data: ClinicalData):
    prediction = predict_patient_risk(data.dict())
    return prediction
