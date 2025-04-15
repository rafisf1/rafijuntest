from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
import joblib
import pandas as pd
from pathlib import Path

app = FastAPI(
    title="LA Real Estate Prediction API",
    description="API for predicting property prices and days on market in Los Angeles",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Load models
try:
    price_model = joblib.load("price_model.pkl")
    dom_model = joblib.load("dom_model.pkl")
except Exception as e:
    print(f"Error loading models: {str(e)}")
    raise

class Property(BaseModel):
    sqft: int
    bedrooms: int
    bathrooms: float
    year_built: int
    zipcode: str

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/predict")
async def predict(data: Property):
    try:
        # Create DataFrame with input data
        df = pd.DataFrame([data.dict()])
        
        # One-hot encode categorical variables
        df = pd.get_dummies(df)
        
        # Make predictions
        price = price_model.predict(df)[0]
        dom = dom_model.predict(df)[0]
        
        return {
            "predicted_price": float(price),
            "predicted_dom": float(dom),
            "input_features": data.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 