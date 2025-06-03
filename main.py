from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import pandas as pd
from prophet import Prophet

app = FastAPI()

class UsageHistory(BaseModel):
    ingredient: str
    dates: List[str]
    quantities: List[float]

class ForecastRequest(BaseModel):
    history: List[UsageHistory]

@app.post("/forecast")
def forecast(req: ForecastRequest):
    results = []
    for item in req.history:
        df = pd.DataFrame({'ds': item.dates, 'y': item.quantities})
        m = Prophet()
        m.fit(df)
        future = m.make_future_dataframe(periods=7)
        forecast = m.predict(future)
        results.append({
            'ingredient': item.ingredient,
            'forecast': forecast[['ds', 'yhat']].tail(7).to_dict(orient='records')
        })
    return results