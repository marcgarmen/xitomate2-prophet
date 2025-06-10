from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Any
import pandas as pd
from prophet import Prophet

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UsageHistory(BaseModel):
    ingredient: Optional[str] = None
    dates: Optional[List[str]] = None
    quantities: Optional[List[float]] = None

class SalesHistory(BaseModel):
    date: str
    total: float

class ForecastRequest(BaseModel):
    history: List[Any]  # Puede ser UsageHistory o SalesHistory

@app.post("/forecast")
def forecast(req: ForecastRequest):
    try:
        print("REQ:", req.history)
        results = []
        # Si es forecast de ventas (lista de dicts con 'date' y 'total')
        if req.history and isinstance(req.history[0], dict) and 'total' in req.history[0]:
            df = pd.DataFrame(req.history)
            print("DF:", df)
            df = df.rename(columns={'date': 'ds', 'total': 'y'})
            if len(df) < 2:
                return []
            m = Prophet()
            m.fit(df)
            future = m.make_future_dataframe(periods=7)
            forecast_df = m.predict(future)
            forecast = forecast_df[['ds', 'yhat']].tail(7).to_dict(orient='records')
            return forecast
        # Si es forecast de ingredientes (lista de UsageHistory)
        for item in req.history:
            if 'ingredient' in item and 'dates' in item and 'quantities' in item:
                df = pd.DataFrame({'ds': item['dates'], 'y': item['quantities']})
                if len(df) < 2:
                    continue
                m = Prophet()
                m.fit(df)
                future = m.make_future_dataframe(periods=7)
                forecast = m.predict(future)
                results.append({
                    'ingredient': item['ingredient'],
                    'forecast': forecast[['ds', 'yhat']].tail(7).to_dict(orient='records')
                })
        return results
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
