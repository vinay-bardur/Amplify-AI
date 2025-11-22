import logging
import json
import time

log = logging.getLogger('amplifyai.sensors.mqtt')

_latest = {}

def _on_message(client, userdata, msg):
    """Internal MQTT message handler."""
    try:
        data = json.loads(msg.payload.decode('utf-8'))
        _latest[msg.topic] = data
    except Exception as e:
        log.exception(f'Malformed MQTT payload on {msg.topic}: {e}')

def start_listener(broker='localhost', port=1883, topics=None, timeout=2):
    """Start MQTT listener in background thread."""
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        log.warning("paho-mqtt not installed")
        return False
    
    if not topics:
        topics = ["site/+/telemetry"]
    
    try:
        client = mqtt.Client()
        client.on_message = _on_message
        client.connect(broker, port, keepalive=60)
        
        for topic in topics:
            client.subscribe(topic)
        
        client.loop_start()
        log.info(f"MQTT listener started: {broker}:{port}")
        return True
    except Exception as e:
        log.warning(f"MQTT connection error: {e}")
        return False

def get_latest(topic: str = None):
    """Get latest MQTT data."""
    if topic:
        return _latest.get(topic, {})
    return _latest
