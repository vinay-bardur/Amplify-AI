# AmplifyAI — Precision Energy Intelligence

## Overview
AmplifyAI is a minimal, beautifully engineered Python MVP that forecasts next-hour solar output and performs clean, intuitive battery optimization. Designed to run anywhere — even offline — with clarity, precision, and zero friction.

**Design Philosophy**: Think Apple. Every part of the system is simple, purposeful, and elegant. No clutter. No unnecessary complexity. Just a powerful core experience executed with precision.

## Current State
- **Status**: Fully operational ✓
- **Last Updated**: November 22, 2025
- **Version**: 1.0 MVP

## How to Run
Simply execute: `python main.py`

The system automatically:
1. Attempts to fetch real NASA POWER solar data
2. Gracefully falls back to local sample dataset if unavailable
3. Trains a linear regression model on the data
4. Forecasts next-hour solar production
5. Recommends battery charge/discharge action

## Recent Changes
- **2025-11-22**: Initial MVP implementation
  - Created all core modules (data_fetcher, modeling, optimizer, main)
  - Implemented NASA POWER API integration with graceful fallback and JSON parsing
  - Built simple linear regression forecasting model
  - Implemented clean rule-based battery optimization logic
  - Designed beautiful terminal output format
  - Added comprehensive optimizer tests covering surplus, deficit, and balanced scenarios

## Project Architecture

### File Structure
```
AmplifyAI/
├── main.py                    # Entry point - orchestrates everything
├── data_fetcher.py            # NASA API + local fallback data loader
├── modeling.py                # Linear regression forecaster
├── optimizer.py               # PuLP battery optimization logic
├── sample_data/
│   └── solar_sample.csv       # Local fallback dataset (13 hours)
├── tests/
│   ├── test_basic.py          # Basic smoke test
│   └── test_optimizer.py      # Optimizer scenario tests
├── requirements.txt           # Python dependencies
└── README.md                  # User documentation
```

### Core Components

**data_fetcher.py**
- `fetch_nasa_power()`: Attempts to retrieve real solar data from NASA POWER API
- `load_sample_data()`: Loads local CSV fallback dataset
- Design: Calm failover - no crashes, always returns usable data

**modeling.py**
- `train_simple_regressor()`: Trains sklearn LinearRegression on historical data
- `predict_next()`: Forecasts next hour production using trained model
- Features: hour, GHI (solar irradiance), temperature, cloud percentage

**optimizer.py**
- `simple_battery_opt()`: Clean rule-based battery optimization
- Handles three scenarios: deficit (discharge), surplus (charge), balanced (hold)
- Constraints: battery capacity, state of charge limits

**main.py**
- Orchestrates the full pipeline
- Displays beautiful, minimal terminal output
- Shows forecast, demand, and battery recommendation with clear reasoning

### Dependencies
- **pandas**: Data manipulation
- **numpy**: Numerical operations  
- **scikit-learn**: Machine learning (LinearRegression)
- **requests**: HTTP API calls for NASA POWER data

## User Preferences
- Pure command-line tool (no web UI, no charts, no dashboards)
- Minimal, elegant terminal output inspired by Apple design philosophy
- Automatic fallback mechanisms - no friction, no errors
- Offline-first design - works without internet

## Technical Decisions
- **Forecasting Model**: Linear regression (simple, fast, interpretable)
- **Optimization**: Rule-based logic (surplus/deficit/balanced - no external solver needed)
- **Data Source**: NASA POWER JSON API with local CSV fallback
- **Error Handling**: Graceful degradation - always returns useful output
- **Output Format**: Clean box-style terminal formatting with clear sections
- **Testing**: Comprehensive optimizer tests ensure correct behavior for all scenarios

## Extension Points
- Replace `data_fetcher.py` to integrate real sensors, APIs, or hardware
- Swap forecasting model in `modeling.py` for more sophisticated algorithms
- Extend `optimizer.py` for multi-hour planning or cost optimization
- Add command-line arguments for custom locations and battery parameters
