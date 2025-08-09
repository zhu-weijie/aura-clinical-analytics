from fastapi import FastAPI
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from aura_core.model.predictor import predict_patient_risk
from aura_core.model.llm.summarizer import summarize_note, load_summarization_model
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter

PREDICTIONS_TOTAL = Counter(
    "aura_predictions_total", "Total number of patient risk predictions made."
)
LLM_SUMMARIZATIONS_TOTAL = Counter(
    "aura_llm_summarizations_total",
    "Total number of clinical note summarizations made by the LLM.",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("API Lifespan: Startup event triggered. Loading models...")
    load_summarization_model()
    yield
    print("API Lifespan: Shutdown event triggered.")


app = FastAPI(title="AURA Prediction API", lifespan=lifespan)

Instrumentator().instrument(app).expose(app)


class ClinicalData(BaseModel):
    patient_id: str
    timestamp: str
    heart_rate: int
    blood_pressure: str
    spo2: float = Field(..., gt=0, lt=1)


class ClinicalNote(BaseModel):
    patient_id: str
    note_text: str = Field(..., min_length=10)


@app.get("/")
def read_root():
    return {"message": "AURA Prediction API is running."}


@app.post("/predict")
def predict(data: ClinicalData):
    PREDICTIONS_TOTAL.inc()
    prediction = predict_patient_risk(data.dict())
    return prediction


@app.post("/summarize")
def summarize_clinical_note(note: ClinicalNote):
    LLM_SUMMARIZATIONS_TOTAL.inc()
    summary = summarize_note(note.note_text)
    return {
        "patient_id": note.patient_id,
        "original_note_length": len(note.note_text),
        "summary": summary,
        "summary_length": len(summary),
    }
