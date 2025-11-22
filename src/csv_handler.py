import pandas as pd
import io

REQUIRED_COLUMNS = {'hour', 'ghi', 'temp_c', 'cloud_pct', 'output_kwh'}

def validate_csv(file_content):
    """Validate uploaded CSV file"""
    try:
        df = pd.read_csv(io.StringIO(file_content.decode('utf-8')))
        
        if len(df) < 5:
            return None, "CSV must have at least 5 rows"
        
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            return None, f"Missing columns: {', '.join(missing)}"
        
        df = df[list(REQUIRED_COLUMNS)]
        
        if df.isnull().any().any():
            df = df.fillna(df.mean(numeric_only=True))
        
        return df, None
    except Exception as e:
        return None, str(e)

def parse_csv_upload(uploaded_file):
    """Parse uploaded CSV file from Streamlit"""
    try:
        df = pd.read_csv(uploaded_file)
        
        if len(df) < 5:
            return None, "CSV must have at least 5 rows"
        
        missing = REQUIRED_COLUMNS - set(df.columns)
        if missing:
            return None, f"Missing columns: {', '.join(missing)}"
        
        df = df[list(REQUIRED_COLUMNS)]
        
        if df.isnull().any().any():
            df = df.fillna(df.mean(numeric_only=True))
        
        return df, None
    except Exception as e:
        return None, str(e)
