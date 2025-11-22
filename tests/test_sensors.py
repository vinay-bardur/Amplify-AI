import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sensors.ingest import ingest_latest
from src.sensors import inverter_api, battery_bms

def test_ingest_latest():
    """Test that ingest_latest returns correct structure."""
    data = ingest_latest()
    assert isinstance(data, dict)
    assert 'inverter' in data
    assert 'bms' in data
    assert 'timestamp' in data
    print("✓ Ingest latest test passed")

def test_inverter_mock():
    """Test mock inverter returns valid data."""
    result = inverter_api.fetch_fronius_status("mock")
    assert result is not None
    assert 'ts' in result
    assert 'pv_power_kw' in result
    assert result['pv_power_kw'] >= 0
    print("✓ Inverter mock test passed")

def test_bms_mock():
    """Test mock BMS returns valid data."""
    result = battery_bms.read_bms_mock()
    assert result is not None
    assert 'ts' in result
    assert 'soc_kwh' in result
    assert 0 <= result['soc_kwh'] <= 50
    print("✓ BMS mock test passed")

def test_inverter_data_types():
    """Test inverter mock data has correct types."""
    result = inverter_api.fetch_fronius_status("mock")
    assert isinstance(result['pv_power_kw'], (int, float))
    assert isinstance(result['pv_voltage'], (int, float))
    print("✓ Inverter data types test passed")

def test_bms_data_types():
    """Test BMS mock data has correct types."""
    result = battery_bms.read_bms_mock()
    assert isinstance(result['soc_kwh'], (int, float))
    assert isinstance(result['voltage'], (int, float))
    print("✓ BMS data types test passed")

if __name__ == '__main__':
    test_ingest_latest()
    test_inverter_mock()
    test_bms_mock()
    test_inverter_data_types()
    test_bms_data_types()
    print("\n✅ All sensor tests passed!")
