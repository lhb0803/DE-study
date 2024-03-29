
import pandas as pd
from pycaret.classification import load_model, predict_model
from fastapi import FastAPI
import uvicorn

# Create the app
app = FastAPI()

# Load trained Pipeline
model = load_model('lgbm_api')

# Define predict function
@app.post('/predict')
def predict(candle_date_time_kst, open, high, low, close, volume, sentiment, new_author_rate, heavy_author_rate):
    data = pd.DataFrame([[candle_date_time_kst, open, high, low, close, volume, sentiment, new_author_rate, heavy_author_rate]])
    data.columns = ['candle_date_time_kst', 'open', 'high', 'low', 'close', 'volume', 'sentiment', 'new_author_rate', 'heavy_author_rate']
    predictions = predict_model(model, data=data) 
    return {'prediction': list(predictions['Label'])}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)