from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
from prophet import Prophet
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class UsageHistory(BaseModel):
    ingredient: str
    dates: List[str]
    quantities: List[float]

class ForecastRequest(BaseModel):
    history: List[UsageHistory]

@app.post("/forecast")
async def forecast(req: ForecastRequest):
    try:
        results = []
        for item in req.history:
            try:
                # Validar datos
                if not item.dates or not item.quantities:
                    raise ValueError(f"No data provided for ingredient {item.ingredient}")
                
                if len(item.dates) != len(item.quantities):
                    raise ValueError(f"Dates and quantities must have the same length for ingredient {item.ingredient}")

                # Crear DataFrame
                df = pd.DataFrame({'ds': item.dates, 'y': item.quantities})
                
                # Configurar y entrenar modelo
                m = Prophet(
                    yearly_seasonality=False,
                    weekly_seasonality=True,
                    daily_seasonality=True
                )
                m.fit(df)
                
                # Generar pronóstico
                future = m.make_future_dataframe(periods=7)
                forecast = m.predict(future)
                
                # Formatear resultado
                forecast_data = forecast[['ds', 'yhat']].tail(7)
                forecast_list = [
                    {
                        'date': row['ds'].strftime('%Y-%m-%d'),
                        'predicted_quantity': float(row['yhat'])
                    }
                    for _, row in forecast_data.iterrows()
                ]
                
                results.append({
                    'ingredient': item.ingredient,
                    'forecast': forecast_list
                })
                
            except Exception as e:
                logger.error(f"Error processing ingredient {item.ingredient}: {str(e)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Error processing ingredient {item.ingredient}: {str(e)}"
                )
        
        return results
        
    except Exception as e:
        logger.error(f"Error in forecast endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating forecast: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)