import os
import json
import time
import signal
import sys
import logging
from typing import Optional

import hid
import paho.mqtt.client as mqtt

from do import Response, TempHum

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("RS5002MQTT")

# =================================================================
# ZUGANGSDATEN (HA OPTIONS ODER UMGEBUNGSVARIABLEN)
# =================================================================
OPTIONS_FILE = "/data/options.json"
if os.path.exists(OPTIONS_FILE):
    with open(OPTIONS_FILE) as f:
        options = json.load(f)
    CONFIG_MQTT_HOST = options.get('mqtt_host', 'core-mosquitto')
    CONFIG_MQTT_USER = options.get('mqtt_user', '')
    CONFIG_MQTT_PASSWORD = options.get('mqtt_password', '')
    READ_INTERVAL = int(options.get('read_interval', 60))
else:
    CONFIG_MQTT_HOST = os.environ.get('MQTT_HOST', 'core-mosquitto')
    CONFIG_MQTT_USER = os.environ.get('MQTT_USER', '')
    CONFIG_MQTT_PASSWORD = os.environ.get('MQTT_PASSWORD', '')
    READ_INTERVAL = int(os.environ.get('READ_INTERVAL', 60))
# =================================================================

MQTT_AVAILABILITY_TOPIC = "rs500/status"
RUNNING = True

def handle_sigterm(signo, frame):
    global RUNNING
    logger.info(f"Signal {signo} erhalten. Beende Add-on sauber...")
    RUNNING = False

signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

def publish_ha_discovery_config(mqtt_client):
    """
    Publiziert die Konfiguration für 8 Geräte mit je 2 Sensoren
    für die automatische Erkennung in Home Assistant.
    """
    logger.info("Publiziere Home Assistant MQTT Discovery Konfiguration für 8 Geräte...")
    for channel in range(1, 9):
        device_info = {
            "identifiers": [f"rs500_channel_{channel}"],
            "name": f"RS500 Sensor Kanal {channel}",
            "manufacturer": "ELV",
            "model": "RS500 Sensor"
        }
        base_topic = f"rs500/channel_{channel}"
        state_topic = f"{base_topic}/state"
        unique_id_base = f"rs500_ch{channel}"
        
        # Temperatur Sensor
        temp_config_topic = f"homeassistant/sensor/{unique_id_base}_temperature/config"
        temp_payload = {
            "name": "Temperatur",
            "unique_id": f"{unique_id_base}_temp",
            "state_topic": state_topic,
            "value_template": "{{ value_json.temperature }}",
            "device_class": "temperature",
            "unit_of_measurement": "°C",
            "availability_topic": MQTT_AVAILABILITY_TOPIC,
            "device": device_info
        }
        mqtt_client.publish(temp_config_topic, json.dumps(temp_payload), retain=True)
        
        # Luftfeuchtigkeit Sensor
        hum_config_topic = f"homeassistant/sensor/{unique_id_base}_humidity/config"
        hum_payload = {
            "name": "Luftfeuchtigkeit",
            "unique_id": f"{unique_id_base}_hum",
            "state_topic": state_topic,
            "value_template": "{{ value_json.humidity }}",
            "device_class": "humidity",
            "unit_of_measurement": "%",
            "availability_topic": MQTT_AVAILABILITY_TOPIC,
            "device": device_info
        }
        mqtt_client.publish(hum_config_topic, json.dumps(hum_payload), retain=True)

class Rs500Reader:
    def __init__(self, vendor_id=0x0483, product_id=0x5750):
        self.__vendor = vendor_id
        self.__product = product_id
        self.__path = None

    def __find_device_path(self):
        devices = hid.enumerate()
        for device in devices:
            if device['vendor_id'] == self.__vendor and device['product_id'] == self.__product:
                self.__path = device['path']
                return
        self.__path = None

    def __query(self) -> Optional[list]:
        if self.__path is None: 
            self.__find_device_path()
            
        if self.__path is None:
            logger.error(f"Gerät mit VID={self.__vendor} und PID={self.__product} nicht gefunden.")
            return None
            
        try:
            rs500_hid = hid.device()
            rs500_hid.open_path(self.__path)
            rs500_hid.set_nonblocking(1)
            command = bytes([0x7B, 0x03, 0x40, 0x7D] + [0] * 60)
            rs500_hid.write(command)
            time.sleep(0.75)
            data = []
            while True:
                d = rs500_hid.read(64)
                if d: 
                    data.extend(d)
                else: 
                    break
            rs500_hid.close()
            return data
        except (IOError, ValueError) as e:
            logger.error(f'Lesefehler am USB Gerät: "{e}"')
            self.__path = None
            return None

    def get_data(self) -> Optional[Response]:
        data = self.__query()
        if data is None: 
            return None
            
        if len(data) != 64:
            logger.error(f"Ungültige Länge der Daten: {len(data)}")
            return None
            
        response = Response()
        channel = 0
        for i in range(1, 24, 3):
            channel += 1
            t1 = data[i]
            t2 = data[i + 1]
            hu = data[i + 2]
            if not (t1 == 0x7F and t2 == 0xFF and hu == 0xFF):
                response.set_channel_data(channel, TempHum.from_protocol([t1, t2], hu))
        return response

if __name__ == "__main__":
    logger.info("Starte RS5002MQTT Add-on...")
    
    client = mqtt.Client("RS5002MQTT")
    client.username_pw_set(CONFIG_MQTT_USER, CONFIG_MQTT_PASSWORD)
    
    # Last Will and Testament (LWT)
    client.will_set(MQTT_AVAILABILITY_TOPIC, payload="offline", retain=True)
    
    connected = False
    while not connected and RUNNING:
        try:
            logger.info(f"Verbinde mit MQTT Broker: {CONFIG_MQTT_HOST}")
            client.connect(CONFIG_MQTT_HOST, 1883, 60)
            client.loop_start()
            connected = True
        except Exception as e:
            logger.error(f"Fehler bei der Verbindung zum MQTT Broker: {e}. Versuche es in 10s erneut...")
            time.sleep(10)

    if not RUNNING:
        sys.exit(0)

    client.publish(MQTT_AVAILABILITY_TOPIC, payload="online", retain=True)
    publish_ha_discovery_config(client)
    
    reader = Rs500Reader()
    logger.info(f"Starte Hauptschleife zum Auslesen der Daten (Intervall: {READ_INTERVAL}s)...")
    
    while RUNNING:
        sensor_data = reader.get_data()
        if sensor_data:
            logger.debug("Daten erfolgreich ausgelesen, publiziere via MQTT...")
            for channel, data in sensor_data.all.items():
                if data:
                    topic = f"rs500/channel_{channel}/state"
                    payload = {"temperature": data.temperature, "humidity": data.humidity}
                    client.publish(topic, json.dumps(payload), retain=True)
                    logger.info(f"-> Daten für Kanal {channel} (T: {data.temperature}°C, H: {data.humidity}%) publiziert.")
        else:
            logger.warning("Keine Daten vom Sensor erhalten, oder Sensor nicht angeschlossen.")
            
        # Warte READ_INTERVAL Sekunden, überprüfe aber öfter ob wir beenden sollen
        for _ in range(READ_INTERVAL):
            if not RUNNING:
                break
            time.sleep(1)

    # Clean Shutdown
    logger.info("Führe Shutdown durch...")
    client.publish(MQTT_AVAILABILITY_TOPIC, payload="offline", retain=True)
    client.loop_stop()
    client.disconnect()
    logger.info("Add-on beendet.")
