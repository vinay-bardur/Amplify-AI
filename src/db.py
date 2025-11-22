import sqlite3
import json
from datetime import datetime
import os

DB_PATH = 'amplifyai.db'

def init_db():
    """Initialize database with required tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS forecast_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            location_lat REAL,
            location_lon REAL,
            model_used TEXT,
            forecast_json TEXT,
            actual_json TEXT,
            mse REAL,
            created_at TEXT
        )''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS battery_schedule_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            horizon_hours INTEGER,
            objective TEXT,
            schedule_json TEXT,
            summary_json TEXT,
            created_at TEXT
        )''')
        
        conn.commit()
        conn.close()
    except Exception as e:
        pass

def insert_forecast(lat, lon, model_used, forecast_data, mse):
    """Insert forecast record into database"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        forecast_json = json.dumps(forecast_data)
        
        c.execute('''INSERT INTO forecast_history 
                     (timestamp, location_lat, location_lon, model_used, forecast_json, mse, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (timestamp, lat, lon, model_used, forecast_json, mse, timestamp))
        
        conn.commit()
        conn.close()
    except Exception:
        pass

def insert_schedule(horizon_hours, objective, schedule_data, summary):
    """Insert battery schedule record into database"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        schedule_json = json.dumps(schedule_data)
        summary_json = json.dumps(summary)
        
        c.execute('''INSERT INTO battery_schedule_history 
                     (timestamp, horizon_hours, objective, schedule_json, summary_json, created_at)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (timestamp, horizon_hours, objective, schedule_json, summary_json, timestamp))
        
        conn.commit()
        conn.close()
    except Exception:
        pass

def load_recent_forecasts(limit=10):
    """Load recent forecasts from database"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''SELECT timestamp, model_used, forecast_json, mse, created_at 
                     FROM forecast_history 
                     ORDER BY created_at DESC LIMIT ?''', (limit,))
        
        rows = c.fetchall()
        conn.close()
        
        forecasts = []
        for row in rows:
            forecasts.append({
                'timestamp': row[0],
                'model': row[1],
                'forecast': json.loads(row[2]),
                'mse': row[3],
                'created_at': row[4]
            })
        
        return forecasts
    except Exception:
        return []

def load_recent_schedules(limit=5):
    """Load recent battery schedules from database"""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''SELECT timestamp, horizon_hours, objective, schedule_json, summary_json, created_at 
                     FROM battery_schedule_history 
                     ORDER BY created_at DESC LIMIT ?''', (limit,))
        
        rows = c.fetchall()
        conn.close()
        
        schedules = []
        for row in rows:
            schedules.append({
                'timestamp': row[0],
                'horizon': row[1],
                'objective': row[2],
                'schedule': json.loads(row[3]),
                'summary': json.loads(row[4]),
                'created_at': row[5]
            })
        
        return schedules
    except Exception:
        return []
