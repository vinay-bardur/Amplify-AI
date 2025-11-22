import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from src.data_fetcher import load_sample_data
from src.modeling import train_simple_regressor, predict_next, forecast_hours

def test_single_hour_forecast():
    """Test single hour prediction"""
    df = load_sample_data()
    features = ['hour', 'ghi', 'temp_c', 'cloud_pct']
    model, mse = train_simple_regressor(df, features, 'output_kwh')
    
    assert mse >= 0
    
    test_row = [12, 950, 33, 3]
    pred = predict_next(model, test_row)
    
    assert pred >= 0
    assert pred <= 10
    print(f"✓ Single hour forecast test passed (prediction: {pred:.2f} kWh)")


def test_multi_hour_forecast():
    """Test multi-hour forecast function"""
    df = load_sample_data()
    features = ['hour', 'ghi', 'temp_c', 'cloud_pct']
    model, mse = train_simple_regressor(df, features, 'output_kwh')
    
    forecast_data = forecast_hours(model, df, features, n_hours=24)
    
    assert 'hours' in forecast_data
    assert 'mean' in forecast_data
    assert 'std' in forecast_data
    
    assert len(forecast_data['hours']) == 24
    assert len(forecast_data['mean']) == 24
    assert len(forecast_data['std']) == 24
    
    assert all(f >= 0 for f in forecast_data['mean'])
    assert all(s >= 0 for s in forecast_data['std'])
    
    print(f"✓ Multi-hour forecast test passed (24 hours forecasted)")


def test_forecast_hours_range():
    """Test various forecast horizons"""
    df = load_sample_data()
    features = ['hour', 'ghi', 'temp_c', 'cloud_pct']
    model, mse = train_simple_regressor(df, features, 'output_kwh')
    
    for n_hours in [6, 12, 24, 48]:
        forecast_data = forecast_hours(model, df, features, n_hours=n_hours)
        assert len(forecast_data['mean']) == n_hours
        print(f"✓ Forecast horizon {n_hours}h test passed")


if __name__ == '__main__':
    test_single_hour_forecast()
    test_multi_hour_forecast()
    test_forecast_hours_range()
    print("\n✅ All forecast tests passed!")
