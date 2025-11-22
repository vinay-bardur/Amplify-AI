# AmplifyAI — Precision Energy Intelligence

**Phase 2**: Multi-hour solar forecasting and battery optimization with Apple-level clarity

AmplifyAI is a validated product prototype combining solar production forecasting with advanced multi-hour battery optimization. Built with a robust engine and polished Streamlit UI, it provides clear, actionable energy management recommendations.

---

## 🚀 Quick Start

### Option 1: Streamlit UI (Recommended)
```bash
python main.py
```
or
```bash
streamlit run app.py
```

This launches the interactive web UI with:
- 📈 24-hour solar forecast with confidence bands
- ⚡ Multi-hour battery optimization scheduler
- 📊 Performance history tracking (preview)

### Option 2: CLI Mode (Power Users)
```bash
python main.py --cli
```

Runs the Phase 1 command-line interface for single-hour forecast and battery recommendation.

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

**Dependencies:**
- pandas, numpy, scikit-learn, requests
- streamlit, altair
- pulp, pytest

---

## 🎯 Features

### Phase 1 (CLI)
- Single-hour solar production forecast
- Linear regression model
- Battery charge/discharge recommendation
- NASA POWER API integration with local fallback
- Beautiful terminal output

### Phase 2 (Streamlit UI)
- **Forecast Tab**: 24-hour solar production forecast with confidence bands
- **Optimize Tab**: Multi-hour battery scheduling using linear programming
- **History Tab**: Performance tracking (preview - full implementation coming soon)
- Interactive parameter controls
- Downloadable forecast and schedule exports as CSV
- Conservative confidence estimates with uncertainty bands

---

## 🧪 Testing

Run all tests:
```bash
pytest tests/
```

**Test Coverage:**
- ✅ Single-hour optimization (surplus, deficit, balanced)
- ✅ Multi-hour LP scheduling (minimize unmet, maximize self-consumption)
- ✅ Battery constraint validation
- ✅ Multi-hour forecast generation (6h, 12h, 24h, 48h horizons)

---

## 🏗️ Architecture

```
AmplifyAI/
├── app.py                              # Streamlit UI (Phase 2)
├── main.py                             # Entry point (CLI + Streamlit modes)
├── src/
│   ├── data_fetcher.py                 # NASA API + local data loader
│   ├── modeling.py                     # Linear regression + multi-hour forecast
│   ├── optimizer.py                    # Phase 1 simple optimizer
│   └── multi_hour_optimizer.py         # Phase 2 LP optimizer (PuLP)
├── sample_data/
│   └── solar_sample.csv                # Local fallback dataset
├── tests/
│   ├── test_basic.py                   # Smoke test
│   ├── test_optimizer.py               # Phase 1 optimizer tests
│   ├── test_multi_hour_optimizer.py    # Phase 2 LP tests
│   └── test_forecast.py                # Forecast tests
├── .streamlit/
│   └── config.toml                     # Streamlit configuration
├── requirements.txt
└── README.md
```

---

## 🎨 Design Philosophy

**Think Apple.** Every output, chart, and recommendation is:
- **Minimal**: No clutter, only essential information
- **Purposeful**: Every element serves a clear function
- **Explainable**: Conservative confidence, clear reasoning

**Conservative Estimates**: The UI always reminds users:
> "This is an estimate — validate with sensors before action."

---

**AmplifyAI Phase 2** — Where precision meets purpose. 🌞⚡
