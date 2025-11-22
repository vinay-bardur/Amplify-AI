def simple_battery_opt(predicted_kwh, expected_kwh, battery_capacity_kwh=100, soc_kwh=50, roundtrip_eff=0.9):
    deficit = expected_kwh - predicted_kwh
    
    if deficit > 0.1:
        available_discharge = min(soc_kwh, deficit)
        return {'charge_kwh': 0.0, 'discharge_kwh': available_discharge}
    
    elif deficit < -0.1:
        surplus = abs(deficit)
        available_capacity = battery_capacity_kwh - soc_kwh
        charge_amount = min(surplus, available_capacity)
        return {'charge_kwh': charge_amount, 'discharge_kwh': 0.0}
    
    else:
        return {'charge_kwh': 0.0, 'discharge_kwh': 0.0}
