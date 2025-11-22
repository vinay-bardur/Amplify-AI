# AmplifyAI — Precision Energy Intelligence

AmplifyAI is crafted to be a clean, minimal, and intuitive MVP. It forecasts next-hour solar output and executes a simple, elegant battery optimization simulation.

## Run
1. Open console
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

The system automatically attempts to fetch real NASA POWER data. If unavailable, it gracefully falls back to the local sample dataset — no errors, no friction.

## Output
- A next-hour solar forecast (kWh)
- A clear, human-friendly battery recommendation

## Notes
- Designed for extensibility. Replace `data_fetcher.py` anytime to integrate real sensors, APIs, or hardware.
