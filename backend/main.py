from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import model
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CarPredictionRequest(BaseModel):
    brand: str
    model: str
    model_year: int
    milage: int
    fuel_type: str
    engine: str
    transmission: str
    accident: str

@app.on_event("startup")
def startup_event():
    if not os.path.exists(model.MODEL_PATH):
        model.train_model()

@app.get("/metadata")
def get_metadata_endpoint():
    return model.get_metadata()

@app.post("/predict")
def predict_price(request: CarPredictionRequest):
    try:
        price = model.predict(request.dict())
        return {"price": price}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
