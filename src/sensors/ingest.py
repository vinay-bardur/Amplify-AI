import os
import yaml
import time
import logging
from . import inverter_api, battery_bms, mqtt_listener

log = logging.getLogger('amplifyai.sensors.ingest')

CONFIG_PATH = os.path.join(os.getcwd(), 'sensor_config.yaml')

def _load_config():
    """Load sensor configuration from YAML."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        log.warning(f"Could not load sensor config: {e}")
        return {}

def ingest_latest():
    """Ingest latest data from all configured sensors."""
    cfg = _load_config()
    data = {
        'inverter': None,
        'bms': None,
        'mqtt': None,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
    }
    
    try:
        inv_cfg = cfg.get('sensors', {}).get('inverter', {})
        provider = inv_cfg.get('provider', 'mock_fronius')
        
        if provider == 'mock_fronius':
            data['inverter'] = inverter_api.fetch_fronius_status(
                inv_cfg.get('api_url'),
                inv_cfg.get('api_key')
            )
        elif provider == 'solaredge':
            data['inverter'] = inverter_api.fetch_solaredge_status(
                inv_cfg.get('api_url'),
                inv_cfg.get('api_key')
            )
    except Exception as e:
        log.exception(f"Inverter ingestion error: {e}")
    
    try:
        bms_cfg = cfg.get('sensors', {}).get('bms', {})
        provider = bms_cfg.get('provider', 'mock_bms')
        
        if provider == 'mock_bms':
            data['bms'] = battery_bms.read_bms_mock()
        elif provider == 'serial':
            data['bms'] = battery_bms.read_bms_serial(bms_cfg.get('connection'))
        elif provider == 'can':
            data['bms'] = battery_bms.read_bms_can(bms_cfg.get('interface', 'can0'))
    except Exception as e:
        log.exception(f"BMS ingestion error: {e}")
    
    try:
        mqtt_cfg = cfg.get('sensors', {}).get('mqtt', {})
        if mqtt_cfg.get('enabled', False):
            mqtt_listener.start_listener(
                mqtt_cfg.get('broker', 'localhost'),
                mqtt_cfg.get('port', 1883),
                mqtt_cfg.get('topics')
            )
            data['mqtt'] = mqtt_listener.get_latest()
    except Exception as e:
        log.exception(f"MQTT ingestion error: {e}")
    
    return data
