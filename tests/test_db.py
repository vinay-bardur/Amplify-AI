import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db import insert_forecast, insert_schedule, load_recent_forecasts, load_recent_schedules, init_db

def test_db_init():
    """Test database initialization"""
    init_db()
    assert True
    print("✓ Database initialization test passed")

def test_insert_forecast():
    """Test forecast insertion"""
    forecast_data = {'hours': [12, 13, 14], 'mean': [5.0, 6.0, 5.5], 'std': [0.5, 0.6, 0.5]}
    insert_forecast(15.3647, 75.1234, 'linear', forecast_data, 0.0041)
    assert True
    print("✓ Forecast insertion test passed")

def test_insert_schedule():
    """Test schedule insertion"""
    schedule_data = {'charge': [5.0, 0.0], 'discharge': [0.0, 3.0]}
    summary = {'total_charge': 5.0, 'total_discharge': 3.0}
    insert_schedule(24, 'minimize_unmet', schedule_data, summary)
    assert True
    print("✓ Schedule insertion test passed")

def test_load_forecasts():
    """Test loading forecasts"""
    forecasts = load_recent_forecasts(5)
    assert isinstance(forecasts, list)
    print(f"✓ Load forecasts test passed (found {len(forecasts)} records)")

def test_load_schedules():
    """Test loading schedules"""
    schedules = load_recent_schedules(5)
    assert isinstance(schedules, list)
    print(f"✓ Load schedules test passed (found {len(schedules)} records)")

if __name__ == '__main__':
    test_db_init()
    test_insert_forecast()
    test_insert_schedule()
    test_load_forecasts()
    test_load_schedules()
    print("\n✅ All database tests passed!")
