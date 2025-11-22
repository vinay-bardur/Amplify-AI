import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetcher import load_sample_data
from src.modeling import train_simple_regressor, train_arima_model, forecast_hours

def test_linear_forecast():
    """Test linear regression forecast"""
    df = load_sample_data()
    features = ['hour', 'ghi', 'temp_c', 'cloud_pct']
    model, mse = train_simple_regressor(df, features, 'output_kwh')
    
    forecast_data = forecast_hours(model, df, features, n_hours=12, model_type='linear')
    
    assert len(forecast_data['mean']) == 12
    assert len(forecast_data['std']) == 12
    assert all(f >= 0 for f in forecast_data['mean'])
    print("✓ Linear forecast test passed")

def test_arima_forecast():
    """Test ARIMA forecast (with fallback)"""
    df = load_sample_data()
    features = ['hour', 'ghi', 'temp_c', 'cloud_pct']
    model, mse = train_simple_regressor(df, features, 'output_kwh')
    
    arima_model = train_arima_model(df)
    
    if arima_model is not None:
        forecast_data = forecast_hours(arima_model, df, features, n_hours=12, model_type='arima')
    else:
        forecast_data = forecast_hours(model, df, features, n_hours=12, model_type='linear')
    
    assert len(forecast_data['mean']) == 12
    print("✓ ARIMA forecast test passed (with fallback)")

def test_prophet_fallback():
    """Test Prophet fallback to linear"""
    df = load_sample_data()
    features = ['hour', 'ghi', 'temp_c', 'cloud_pct']
    model, mse = train_simple_regressor(df, features, 'output_kwh')
    
    forecast_data = forecast_hours(model, df, features, n_hours=12, model_type='prophet')
    
    assert len(forecast_data['mean']) == 12
    print("✓ Prophet fallback test passed")

def test_confidence_intervals():
    """Test confidence interval calculation"""
    df = load_sample_data()
    features = ['hour', 'ghi', 'temp_c', 'cloud_pct']
    model, mse = train_simple_regressor(df, features, 'output_kwh')
    
    forecast_data = forecast_hours(model, df, features, n_hours=24, model_type='linear')
    
    assert all(s > 0 for s in forecast_data['std'])
    assert len(forecast_data['std']) == 24
    print("✓ Confidence intervals test passed")

if __name__ == '__main__':
    test_linear_forecast()
    test_arima_forecast()
    test_prophet_fallback()
    test_confidence_intervals()
    print("\n✅ All model selection tests passed!")
