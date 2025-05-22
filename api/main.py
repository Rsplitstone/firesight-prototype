from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="FireSight API", description="Prototype REST API for FireSight")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Alert(BaseModel):
    id: int
    message: str
    time: str
    status: str

# Mock in-memory data
aaa_alerts = [
    {"id": 1, "message": "Fire spotted near park", "time": "2023-01-01T10:00:00", "status": "new"},
    {"id": 2, "message": "Smoke detected downtown", "time": "2023-01-01T11:00:00", "status": "acknowledged"},
]

feed_summary = {
    "summary": "No critical incidents at this time"
}

class PredictRequest(BaseModel):
    features: List[float]

class PredictResponse(BaseModel):
    prediction: float

@app.get("/alerts", response_model=List[Alert])
def get_alerts() -> List[Alert]:
    """Return current mock alerts."""
    return aaa_alerts

@app.get("/data/summary")
def get_summary() -> dict:
    """Return latest fused feed summary."""
    return feed_summary

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest) -> PredictResponse:
    """Return a simple prediction based on the input."""
    pred_value = sum(req.features)
    return PredictResponse(prediction=pred_value)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
