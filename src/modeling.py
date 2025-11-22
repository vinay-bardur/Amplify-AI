import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

def train_simple_regressor(df, features, target):
    X = df[features].values
    y = df[target].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    return model, mse

def predict_next(model, feature_row):
    x = np.array(feature_row).reshape(1, -1)
    return float(model.predict(x)[0])

def forecast_hours(model, df, features, n_hours=24):
    """
    Forecast next n hours of solar production with confidence estimates.
    
    Args:
        model: Trained regression model
        df: Historical data DataFrame
        features: List of feature names
        n_hours: Number of hours to forecast
    
    Returns:
        dict with 'hours', 'mean', 'std' arrays
    """
    last_row = df.iloc[-1]
    last_hour = int(last_row['hour'])
    
    forecasts = []
    uncertainties = []
    hours_list = []
    
    for i in range(n_hours):
        next_hour = (last_hour + i + 1) % 24
        
        if i == 0:
            base_ghi = last_row['ghi']
            base_temp = last_row['temp_c']
            base_cloud = last_row['cloud_pct']
        else:
            base_ghi = forecasts[-1] * 250.0 if forecasts[-1] > 0 else 0
            base_temp = last_row['temp_c'] + np.random.normal(0, 0.5)
            base_cloud = min(100, max(0, base_cloud + np.random.normal(0, 5)))
        
        if 6 <= next_hour <= 18:
            solar_factor = np.sin((next_hour - 6) * np.pi / 12) ** 0.5
            ghi = base_ghi * solar_factor * (1 - base_cloud / 200.0)
        else:
            ghi = 0
        
        feature_row = [next_hour, max(0, ghi), base_temp, base_cloud]
        pred = predict_next(model, feature_row)
        
        uncertainty = 0.15 * pred + 0.1
        
        forecasts.append(max(0, pred))
        uncertainties.append(uncertainty)
        hours_list.append(next_hour)
    
    return {
        'hours': hours_list,
        'mean': forecasts,
        'std': uncertainties
    }
