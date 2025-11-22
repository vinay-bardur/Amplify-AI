import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.optimizer import simple_battery_opt

def test_deficit_scenario():
    result = simple_battery_opt(predicted_kwh=2.0, expected_kwh=5.0, battery_capacity_kwh=50, soc_kwh=20)
    assert result['discharge_kwh'] == 3.0
    assert result['charge_kwh'] == 0.0
    print("✓ Deficit scenario: Recommends discharge of 3.0 kWh")

def test_surplus_scenario():
    result = simple_battery_opt(predicted_kwh=8.0, expected_kwh=5.0, battery_capacity_kwh=50, soc_kwh=20)
    assert result['charge_kwh'] == 3.0
    assert result['discharge_kwh'] == 0.0
    print("✓ Surplus scenario: Recommends charge of 3.0 kWh")

def test_balanced_scenario():
    result = simple_battery_opt(predicted_kwh=5.0, expected_kwh=5.0, battery_capacity_kwh=50, soc_kwh=20)
    assert result['charge_kwh'] == 0.0
    assert result['discharge_kwh'] == 0.0
    print("✓ Balanced scenario: No action needed")

if __name__ == '__main__':
    test_deficit_scenario()
    test_surplus_scenario()
    test_balanced_scenario()
    print("\nAll optimizer tests passed!")
