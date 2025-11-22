import os
import pandas as pd
import requests
from io import StringIO

def fetch_nasa_power(lat=15.3647, lon=75.1234):
    try:
        url = (
            'https://power.larc.nasa.gov/api/temporal/hourly/point'
            '?parameters=ALLSKY_SFC_SW_DWN,T2M,CLD_FRAC'
            '&community=RE'
            f'&longitude={lon}&latitude={lat}'
            '&start=20240601&end=20240601'
            '&format=JSON'
        )
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            raise Exception('Non-200 response')
        
        data = r.json()
        params = data.get('properties', {}).get('parameter', {})
        
        if not params:
            return None
        
        ghi_data = params.get('ALLSKY_SFC_SW_DWN', {})
        temp_data = params.get('T2M', {})
        cloud_data = params.get('CLD_FRAC', {})
        
        if not (ghi_data and temp_data and cloud_data):
            return None
        
        hours = []
        ghi_vals = []
        temp_vals = []
        cloud_vals = []
        output_vals = []
        
        for hour_key in sorted(ghi_data.keys()):
            hour = int(hour_key) % 100
            if 6 <= hour <= 18:
                ghi = ghi_data.get(hour_key, 0)
                temp = temp_data.get(hour_key, 20)
                cloud = cloud_data.get(hour_key, 50)
                
                output = max(0, ghi / 250.0)
                
                hours.append(hour)
                ghi_vals.append(ghi)
                temp_vals.append(temp)
                cloud_vals.append(cloud * 100)
                output_vals.append(output)
        
        if len(hours) < 5:
            return None
        
        df = pd.DataFrame({
            'hour': hours,
            'ghi': ghi_vals,
            'temp_c': temp_vals,
            'cloud_pct': cloud_vals,
            'output_kwh': output_vals
        })
        
        return df
    
    except Exception:
        return None

def load_sample_data(path='sample_data/solar_sample.csv'):
    return pd.read_csv(path)
