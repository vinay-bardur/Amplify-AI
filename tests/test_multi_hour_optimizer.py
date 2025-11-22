import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.multi_hour_optimizer import optimize_battery_schedule

def test_minimize_unmet_demand():
    """Test that optimizer minimizes unmet demand in deficit scenarios"""
    forecast_kwh = [2.0] * 12
    demand_kwh = [5.0] * 12
    
    result = optimize_battery_schedule(
        forecast_kwh=forecast_kwh,
        demand_kwh=demand_kwh,
        battery_capacity_kwh=50,
        initial_soc_kwh=30,
        charge_rate_max=10,
        discharge_rate_max=10,
        roundtrip_eff=0.9,
        objective='minimize_unmet'
    )
    
    assert result['status'] == 'success'
    assert len(result['discharge']) == 12
    assert all(d >= 0 for d in result['discharge'])
    assert sum(result['discharge']) > 0
    print("✓ Minimize unmet demand test passed")


def test_maximize_self_consumption():
    """Test that optimizer charges battery during surplus"""
    forecast_kwh = [8.0] * 12
    demand_kwh = [5.0] * 12
    
    result = optimize_battery_schedule(
        forecast_kwh=forecast_kwh,
        demand_kwh=demand_kwh,
        battery_capacity_kwh=50,
        initial_soc_kwh=10,
        charge_rate_max=10,
        discharge_rate_max=10,
        roundtrip_eff=0.9,
        objective='maximize_self_consumption'
    )
    
    assert result['status'] == 'success'
    assert len(result['charge']) == 12
    assert all(c >= 0 for c in result['charge'])
    assert sum(result['charge']) > 0
    print("✓ Maximize self-consumption test passed")


def test_battery_constraints():
    """Test that optimizer respects battery capacity and SOC limits"""
    forecast_kwh = [4.0] * 12
    demand_kwh = [2.0] * 12
    battery_capacity = 20.0
    
    result = optimize_battery_schedule(
        forecast_kwh=forecast_kwh,
        demand_kwh=demand_kwh,
        battery_capacity_kwh=battery_capacity,
        initial_soc_kwh=10,
        charge_rate_max=5,
        discharge_rate_max=5,
        roundtrip_eff=0.9
    )
    
    assert result['status'] == 'success'
    assert all(0 <= soc <= battery_capacity for soc in result['soc'])
    assert all(0 <= c <= 5 for c in result['charge'])
    assert all(0 <= d <= 5 for d in result['discharge'])
    print("✓ Battery constraints test passed")


def test_balanced_scenario():
    """Test optimizer with balanced supply and demand"""
    forecast_kwh = [5.0] * 12
    demand_kwh = [5.0] * 12
    
    result = optimize_battery_schedule(
        forecast_kwh=forecast_kwh,
        demand_kwh=demand_kwh,
        battery_capacity_kwh=50,
        initial_soc_kwh=25,
        charge_rate_max=10,
        discharge_rate_max=10,
        roundtrip_eff=0.9
    )
    
    assert result['status'] == 'success'
    total_unmet = sum(result['unmet_demand'])
    assert total_unmet < 0.1
    print(f"✓ Balanced scenario test passed (total unmet: {total_unmet:.4f})")


if __name__ == '__main__':
    test_minimize_unmet_demand()
    test_maximize_self_consumption()
    test_battery_constraints()
    test_balanced_scenario()
    print("\n✅ All multi-hour optimizer tests passed!")
