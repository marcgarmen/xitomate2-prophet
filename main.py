from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Any
import pandas as pd
from prophet import Prophet

app = FastAPI()

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
    results = []
    # Si es forecast de ventas (lista de dicts con 'date' y 'total')
    if req.history and isinstance(req.history[0], dict) and 'total' in req.history[0]:
        df = pd.DataFrame(req.history)
        df = df.rename(columns={'date': 'ds', 'total': 'y'})
        m = Prophet()
        m.fit(df)
        future = m.make_future_dataframe(periods=5)
        forecast_df = m.predict(future)
        # Devuelve los últimos 7 días pronosticados
        forecast = forecast_df[['ds', 'yhat']].tail(5).to_dict(orient='records')
        return forecast
    # Si es forecast de ingredientes (lista de UsageHistory)
    for item in req.history:
        if 'ingredient' in item and 'dates' in item and 'quantities' in item:
            df = pd.DataFrame({'ds': item['dates'], 'y': item['quantities']})
            m = Prophet()
            m.fit(df)
            future = m.make_future_dataframe(periods=5)
            forecast = m.predict(future)
            results.append({
                'ingredient': item['ingredient'],
                'forecast': forecast[['ds', 'yhat']].tail(5).to_dict(orient='records')
            })
    return results