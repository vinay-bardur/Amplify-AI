import logging
import sys
import argparse

from src.data_fetcher import fetch_nasa_power, load_sample_data
from src.modeling import train_simple_regressor, predict_next
from src.optimizer import simple_battery_opt

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger('AmplifyAI')

def build_features_from_row(row):
    return [row['hour'], row['ghi'], row['temp_c'], row['cloud_pct']]


def run_cli():
    """Phase 1 CLI mode - single hour forecast and optimization"""
    log.info('AmplifyAI starting…')

    try:
        net_data = fetch_nasa_power()
        df = net_data if net_data is not None else load_sample_data()
        if net_data is None:
            log.info('Using local sample dataset.')
    except Exception:
        log.warning('Network unavailable — falling back to local sample dataset.')
        df = load_sample_data()

    required = {'hour', 'ghi', 'temp_c', 'cloud_pct', 'output_kwh'}
    if not required.issubset(df.columns):
        log.error('Dataset missing required columns.')
        sys.exit(1)

    features = ['hour', 'ghi', 'temp_c', 'cloud_pct']

    model, mse = train_simple_regressor(df, features, 'output_kwh')
    log.info(f'Model trained (MSE: {mse:.4f})')

    last = df.iloc[-1]
    next_hour = (int(last['hour']) + 1) % 24

    next_row = {
        'hour': next_hour,
        'ghi': max(0, last['ghi'] * 0.9),
        'temp_c': last['temp_c'],
        'cloud_pct': min(100, last['cloud_pct'] * 1.05)
    }

    pred = predict_next(model, build_features_from_row(next_row))

    expected_demand = 5.0
    deficit = expected_demand - pred

    print("\n" + "="*50)
    print("         AmplifyAI Forecast")
    print("="*50)
    print(f"Next hour production: {pred:.2f} kWh")
    print(f"Expected demand:      {expected_demand:.2f} kWh")

    opt = simple_battery_opt(pred, expected_kwh=expected_demand, battery_capacity_kwh=50, soc_kwh=20)

    print("\n" + "="*50)
    print("         Battery Recommendation")
    print("="*50)

    if deficit > 0.5:
        action = f"Discharge {min(deficit, opt['discharge_kwh']):.2f} kWh"
        reason = "Predicted deficit; using battery to stabilize"
    elif deficit < -0.5:
        surplus = abs(deficit)
        action = f"Charge {min(surplus, opt['charge_kwh']):.2f} kWh"
        reason = "Predicted surplus; storing excess energy"
    else:
        action = "Hold steady"
        reason = "Production matches demand; no action needed"

    print(f"Recommendation: {action}")
    print(f"Reason:         {reason}")
    print("="*50 + "\n")


def run_streamlit():
    """Phase 2 Streamlit UI mode - multi-hour forecast and optimization"""
    import subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])


def main():
    parser = argparse.ArgumentParser(
        description='AmplifyAI - Solar Forecasting & Battery Optimization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python main.py             # Launch Streamlit UI (default)
  python main.py --cli       # Run CLI mode (Phase 1)
  python main.py --help      # Show this help message
        '''
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run in CLI mode (Phase 1 single-hour forecast)'
    )
    
    args = parser.parse_args()
    
    if args.cli:
        run_cli()
    else:
        run_streamlit()


if __name__ == '__main__':
    main()
