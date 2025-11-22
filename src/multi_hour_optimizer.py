from pulp import LpProblem, LpVariable, LpMinimize, PULP_CBC_CMD
import numpy as np

def optimize_battery_schedule(
    forecast_kwh,
    demand_kwh,
    battery_capacity_kwh=50,
    initial_soc_kwh=20,
    charge_rate_max=10,
    discharge_rate_max=10,
    roundtrip_eff=0.9,
    objective='minimize_unmet'
):
    """
    Multi-hour battery optimization using Linear Programming.
    
    Args:
        forecast_kwh: List of forecasted solar production (kWh) for each hour
        demand_kwh: List of expected demand (kWh) for each hour
        battery_capacity_kwh: Maximum battery capacity (kWh)
        initial_soc_kwh: Initial state of charge (kWh)
        charge_rate_max: Maximum charge rate (kW)
        discharge_rate_max: Maximum discharge rate (kW)
        roundtrip_eff: Roundtrip efficiency (0-1)
        objective: 'minimize_unmet' or 'maximize_self_consumption'
    
    Returns:
        dict with 'charge', 'discharge', 'soc', 'unmet_demand', 'excess_energy', 'actions'
    """
    horizon = len(forecast_kwh)
    
    if len(demand_kwh) != horizon:
        raise ValueError("Forecast and demand must have same length")
    
    prob = LpProblem('MultiHourBatteryOpt', LpMinimize)
    
    charge = [LpVariable(f'charge_{t}', lowBound=0, upBound=charge_rate_max) for t in range(horizon)]
    discharge = [LpVariable(f'discharge_{t}', lowBound=0, upBound=discharge_rate_max) for t in range(horizon)]
    soc = [LpVariable(f'soc_{t}', lowBound=0, upBound=battery_capacity_kwh) for t in range(horizon)]
    unmet = [LpVariable(f'unmet_{t}', lowBound=0) for t in range(horizon)]
    excess = [LpVariable(f'excess_{t}', lowBound=0) for t in range(horizon)]
    
    if objective == 'minimize_unmet':
        prob += sum(unmet)
    elif objective == 'maximize_self_consumption':
        prob += sum(excess)
    else:
        prob += sum(unmet) + 0.5 * sum(excess)
    
    for t in range(horizon):
        if t == 0:
            prob += soc[t] == initial_soc_kwh + (charge[t] * roundtrip_eff) - discharge[t]
        else:
            prob += soc[t] == soc[t-1] + (charge[t] * roundtrip_eff) - discharge[t]
        
        prob += forecast_kwh[t] + discharge[t] + unmet[t] == demand_kwh[t] + charge[t] + excess[t]
        
        prob += charge[t] + discharge[t] <= max(charge_rate_max, discharge_rate_max)
    
    prob.solve(PULP_CBC_CMD(msg=0))
    
    if prob.status != 1:
        return {
            'charge': [0.0] * horizon,
            'discharge': [0.0] * horizon,
            'soc': [initial_soc_kwh] * horizon,
            'unmet_demand': [max(0, demand_kwh[t] - forecast_kwh[t]) for t in range(horizon)],
            'excess_energy': [max(0, forecast_kwh[t] - demand_kwh[t]) for t in range(horizon)],
            'actions': ['Hold (optimization failed)'] * horizon,
            'status': 'failed'
        }
    
    charge_vals = [charge[t].value() if charge[t].value() else 0.0 for t in range(horizon)]
    discharge_vals = [discharge[t].value() if discharge[t].value() else 0.0 for t in range(horizon)]
    soc_vals = [soc[t].value() if soc[t].value() else 0.0 for t in range(horizon)]
    unmet_vals = [unmet[t].value() if unmet[t].value() else 0.0 for t in range(horizon)]
    excess_vals = [excess[t].value() if excess[t].value() else 0.0 for t in range(horizon)]
    
    actions = []
    for t in range(horizon):
        if charge_vals[t] > 0.1:
            actions.append(f"Charge {charge_vals[t]:.2f} kWh (surplus expected)")
        elif discharge_vals[t] > 0.1:
            actions.append(f"Discharge {discharge_vals[t]:.2f} kWh (deficit expected)")
        else:
            actions.append("Hold steady (balanced)")
    
    return {
        'charge': charge_vals,
        'discharge': discharge_vals,
        'soc': soc_vals,
        'unmet_demand': unmet_vals,
        'excess_energy': excess_vals,
        'actions': actions,
        'status': 'success'
    }
