import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_fetcher import fetch_nasa_power, load_sample_data
from src.modeling import train_simple_regressor, forecast_hours, train_arima_model
from src.multi_hour_optimizer import optimize_battery_schedule
from src.csv_handler import parse_csv_upload
from src.db import insert_forecast, insert_schedule, load_recent_forecasts, load_recent_schedules

st.set_page_config(page_title="AmplifyAI - Solar & Battery Intelligence", layout="wide")

st.title("AmplifyAI")
st.caption("Precision Energy Intelligence — Multi-hour solar forecasting and battery optimization")

@st.cache_data
def load_and_train_model():
    try:
        df_nasa = fetch_nasa_power()
        if df_nasa is not None and len(df_nasa) > 5:
            df = df_nasa
            data_source = "NASA POWER API"
        else:
            df = load_sample_data()
            data_source = "Local Sample Data"
    except Exception:
        df = load_sample_data()
        data_source = "Local Sample Data (fallback)"
    
    features = ['hour', 'ghi', 'temp_c', 'cloud_pct']
    model, mse = train_simple_regressor(df, features, 'output_kwh')
    
    return model, df, mse, data_source

model, df, mse, data_source = load_and_train_model()

st.sidebar.header("Configuration")
st.sidebar.info(f"**Data Source:** {data_source}")
st.sidebar.metric("Model MSE", f"{mse:.4f}")

uploaded_file = st.sidebar.file_uploader("Upload CSV Data", type=['csv'])
if uploaded_file is not None:
    df_uploaded, error = parse_csv_upload(uploaded_file)
    if df_uploaded is not None:
        df = df_uploaded
        st.sidebar.success("CSV loaded successfully")
        features = ['hour', 'ghi', 'temp_c', 'cloud_pct']
        model, mse = train_simple_regressor(df, features, 'output_kwh')
    else:
        st.sidebar.error(f"CSV Error: {error}")

tab1, tab2, tab3 = st.tabs(["Forecast", "Optimize", "History"])

with tab1:
    st.header("24-Hour Solar Forecast")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        horizon_hours = st.slider("Forecast Horizon (hours)", 6, 48, 24)
    
    with col2:
        model_type = st.selectbox("Model", ["linear", "arima", "prophet"])
    
    with col3:
        lat = st.number_input("Latitude", value=15.3647, format="%.4f")
    
    with col4:
        lon = st.number_input("Longitude", value=75.1234, format="%.4f")
    
    if st.button("Refresh Forecast", type="primary"):
        st.cache_data.clear()
        st.rerun()
    
    forecast_data = forecast_hours(model, df, ['hour', 'ghi', 'temp_c', 'cloud_pct'], n_hours=horizon_hours, model_type=model_type)
    
    insert_forecast(lat, lon, model_type, forecast_data, mse)
    
    forecast_df = pd.DataFrame({
        'Hour': forecast_data['hours'],
        'Mean Forecast (kWh)': forecast_data['mean'],
        'Uncertainty (kWh)': forecast_data['std']
    })
    forecast_df['Lower Bound'] = forecast_df['Mean Forecast (kWh)'] - forecast_df['Uncertainty (kWh)']
    forecast_df['Upper Bound'] = forecast_df['Mean Forecast (kWh)'] + forecast_df['Uncertainty (kWh)']
    forecast_df['Lower Bound'] = forecast_df['Lower Bound'].clip(lower=0)
    
    base_chart = alt.Chart(forecast_df).encode(x=alt.X('Hour:Q', title='Hour of Day'))
    
    line = base_chart.mark_line(color='#1f77b4', strokeWidth=3).encode(
        y=alt.Y('Mean Forecast (kWh):Q', title='Solar Production (kWh)')
    )
    
    band = base_chart.mark_area(opacity=0.3, color='#1f77b4').encode(
        y='Lower Bound:Q', y2='Upper Bound:Q'
    )
    
    chart = (band + line).properties(width=800, height=400, title='Solar Production Forecast with Confidence Band')
    st.altair_chart(chart, use_container_width=None)
    
    st.info("Conservative Estimate — This forecast is based on historical patterns. Always validate with real sensors before taking action.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.dataframe(forecast_df[['Hour', 'Mean Forecast (kWh)', 'Uncertainty (kWh)']], width='stretch')
    with col2:
        csv = forecast_df.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv, file_name=f"solar_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")

with tab2:
    st.header("Multi-Hour Battery Optimization")
    
    st.markdown("Configure battery parameters and run optimization to schedule charge/discharge actions over the forecast horizon.")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        battery_capacity = st.number_input("Battery Capacity (kWh)", value=50.0, min_value=1.0, max_value=500.0)
    with col2:
        initial_soc = st.number_input("Initial SOC (kWh)", value=20.0, min_value=0.0, max_value=battery_capacity)
    with col3:
        charge_rate = st.number_input("Max Charge Rate (kW)", value=10.0, min_value=0.1, max_value=100.0)
    with col4:
        discharge_rate = st.number_input("Max Discharge Rate (kW)", value=10.0, min_value=0.1, max_value=100.0)
    
    col1, col2 = st.columns(2)
    with col1:
        efficiency = st.slider("Roundtrip Efficiency", 0.5, 1.0, 0.9, 0.05)
    with col2:
        objective = st.selectbox("Optimization Objective", ["minimize_unmet", "maximize_self_consumption", "balanced"], index=0, format_func=lambda x: {"minimize_unmet": "Minimize Unmet Demand", "maximize_self_consumption": "Maximize Self-Consumption", "balanced": "Balanced Approach"}[x])
    
    opt_horizon = st.slider("Optimization Horizon (hours)", 6, 24, 24)
    constant_demand = st.number_input("Expected Demand per Hour (kWh)", value=5.0, min_value=0.1)
    
    if st.button("Run Optimization", type="primary"):
        forecast_data = forecast_hours(model, df, ['hour', 'ghi', 'temp_c', 'cloud_pct'], n_hours=opt_horizon, model_type='linear')
        forecast_kwh = forecast_data['mean']
        demand_kwh = [constant_demand] * opt_horizon
        
        with st.spinner("Optimizing battery schedule..."):
            result = optimize_battery_schedule(forecast_kwh=forecast_kwh, demand_kwh=demand_kwh, battery_capacity_kwh=battery_capacity, initial_soc_kwh=initial_soc, charge_rate_max=charge_rate, discharge_rate_max=discharge_rate, roundtrip_eff=efficiency, objective=objective)
        
        if result['status'] == 'success':
            st.success("Optimization completed successfully")
            
            schedule_df = pd.DataFrame({
                'Hour': forecast_data['hours'],
                'Forecast (kWh)': forecast_kwh,
                'Demand (kWh)': demand_kwh,
                'Charge (kWh)': result['charge'],
                'Discharge (kWh)': result['discharge'],
                'SOC (kWh)': result['soc'],
                'Action': result['actions']
            })
            
            soc_chart = alt.Chart(schedule_df).mark_line(color='#2ca02c', strokeWidth=3, point=True).encode(x=alt.X('Hour:Q', title='Hour of Day'), y=alt.Y('SOC (kWh):Q', title='Battery State of Charge (kWh)', scale=alt.Scale(domain=[0, battery_capacity]))).properties(width=800, height=300, title='Battery State of Charge Over Time')
            st.altair_chart(soc_chart, use_container_width=None)
            
            charge_discharge_df = schedule_df[['Hour', 'Charge (kWh)', 'Discharge (kWh)']].melt(id_vars=['Hour'], var_name='Action Type', value_name='Energy (kWh)')
            bar_chart = alt.Chart(charge_discharge_df).mark_bar().encode(x=alt.X('Hour:Q', title='Hour of Day'), y=alt.Y('Energy (kWh):Q'), color=alt.Color('Action Type:N', scale=alt.Scale(domain=['Charge (kWh)', 'Discharge (kWh)'], range=['#2ca02c', '#d62728']))).properties(width=800, height=250, title='Charge & Discharge Schedule')
            st.altair_chart(bar_chart, use_container_width=None)
            
            st.subheader("Recommended Actions")
            for idx, row in schedule_df.iterrows():
                if row['Charge (kWh)'] > 0.1 or row['Discharge (kWh)'] > 0.1:
                    with st.expander(f"Hour {row['Hour']}: {row['Action']}"):
                        st.write(f"**Forecast:** {row['Forecast (kWh)']:.2f} kWh")
                        st.write(f"**Demand:** {row['Demand (kWh)']:.2f} kWh")
                        st.write(f"**Battery SOC:** {row['SOC (kWh)']:.2f} kWh")
                        if row['Charge (kWh)'] > 0.1:
                            st.success(f"**Why charge?** Forecast shows {row['Forecast (kWh)'] - row['Demand (kWh)']:.2f} kWh surplus. Store excess energy for later use.")
                        elif row['Discharge (kWh)'] > 0.1:
                            st.warning(f"**Why discharge?** Forecast shows {row['Demand (kWh)'] - row['Forecast (kWh)']:.2f} kWh deficit. Use stored battery energy to meet demand.")
            
            summary = {'total_charge': sum(result['charge']), 'total_discharge': sum(result['discharge']), 'final_soc': result['soc'][-1]}
            insert_schedule(opt_horizon, objective, result, summary)
            
            csv_schedule = schedule_df.to_csv(index=False)
            st.download_button(label="Export Schedule", data=csv_schedule, file_name=f"battery_schedule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv")
        else:
            st.error("Optimization failed. Please check your parameters and try again.")

with tab3:
    st.header("Performance History")
    
    forecasts = load_recent_forecasts(10)
    schedules = load_recent_schedules(5)
    
    if forecasts:
        st.subheader("Recent Forecasts")
        forecast_history_df = pd.DataFrame([
            {'Timestamp': f['timestamp'][:10], 'Model': f['model'], 'MSE': f['mse']}
            for f in forecasts
        ])
        st.dataframe(forecast_history_df, width='stretch')
        
        mse_data = pd.DataFrame([
            {'Date': f['timestamp'][:10], 'MSE': f['mse']}
            for f in forecasts
        ])
        mse_chart = alt.Chart(mse_data).mark_line(point=True).encode(
            x='Date:N', y='MSE:Q'
        ).properties(width=800, height=300, title='Forecast Accuracy Trend (MSE)')
        st.altair_chart(mse_chart, use_container_width=None)
    else:
        st.info("No forecast history yet. Generate forecasts to see history.")
    
    if schedules:
        st.subheader("Recent Battery Schedules")
        schedule_history_df = pd.DataFrame([
            {'Timestamp': s['timestamp'][:10], 'Horizon': s['horizon'], 'Objective': s['objective']}
            for s in schedules
        ])
        st.dataframe(schedule_history_df, width='stretch')
    else:
        st.info("No schedule history yet. Run optimizations to see history.")

st.sidebar.markdown("---")
st.sidebar.markdown("### About AmplifyAI")
st.sidebar.markdown("""
**Phase 3 - Production MVP**

- SQLite persistence
- CSV upload support
- Multi-model forecasting
- Real history tracking
- Confidence intervals

*Always validate recommendations with real sensor data before taking action.*
""")
