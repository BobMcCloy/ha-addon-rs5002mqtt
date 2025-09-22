import os
import json
import time
from sys import stderr
from typing import Optional

import hid
import paho.mqtt.client as mqtt

from do import Response, TempHum

# =================================================================
# FESTE ZUGANGSDATEN HIER EINTRAGEN
# =================================================================
CONFIG_MQTT_HOST = "core-mosquitto"
CONFIG_MQTT_USER = "rs5002mqtt"
CONFIG_MQTT_PASSWORD = "rs5002mqtt"
# =================================================================

READ_INTERVAL = 60

def publish_ha_discovery_config(mqtt_client):
    """
    Publiziert die Konfiguration für 8 Geräte mit je 2 Sensoren
    für die automatische Erkennung in Home Assistant.
    """
    print("Publiziere Home Assistant MQTT Discovery Konfiguration für 8 Geräte...")
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
        temp_config_topic = f"homeassistant/sensor/{unique_id_base}_temperature/config"
        temp_payload = {
            "name": "Temperatur",
            "unique_id": f"{unique_id_base}_temp",
            "state_topic": state_topic,
            "value_template": "{{ value_json.temperature }}",
            "device_class": "temperature",
            "unit_of_measurement": "°C",
            "device": device_info
        }
        mqtt_client.publish(temp_config_topic, json.dumps(temp_payload), retain=True)
        hum_config_topic = f"homeassistant/sensor/{unique_id_base}_humidity/config"
        hum_payload = {
            "name": "Luftfeuchtigkeit",
            "unique_id": f"{unique_id_base}_hum",
            "state_topic": state_topic,
            "value_template": "{{ value_json.humidity }}",
            "device_class": "humidity",
            "unit_of_measurement": "%",
            "device": device_info
        }
        mqtt_client.publish(hum_config_topic, json.dumps(hum_payload), retain=True)

class Rs500Reader(object):
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
    def __query(self) -> list:
        if self.__path is None: self.__find_device_path()
        if self.__path is None:
            print(f"Gerät mit VID={self.__vendor} und PID={self.__product} nicht gefunden.", file=stderr)
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
                if d: data.extend(d)
                else: break
            rs500_hid.close()
            return data
        except (IOError, ValueError) as e:
            print(f'Lesefehler: "{e}"', file=stderr)
            self.__path = None
            return None
    def get_data(self) -> Optional[Response]:
        data = self.__query()
        if data is None: return None
        if len(data) != 64:
            print(f"Ungültige Länge der Daten: {len(data)}", file=stderr)
            return None
        response = Response()
        channel = 0
        for i in range(1, 24, 3):
            channel += 1
            t1 = data[i]; t2 = data[i + 1]; hu = data[i + 2]
            if not (t1 == 0x7F and t2 == 0xFF and hu == 0xFF):
                response.set_channel_data(channel, TempHum.from_protocol([t1, t2], hu))
        return response

if __name__ == "__main__":
    print("Starte RS5002MQTT Add-on...")
    client = mqtt.Client("RS5002MQTT")
    client.username_pw_set(CONFIG_MQTT_USER, CONFIG_MQTT_PASSWORD)
    try:
        print(f"Verbinde mit MQTT Broker: {CONFIG_MQTT_HOST}")
        client.connect(CONFIG_MQTT_HOST, 1883, 60)
        client.loop_start()
    except Exception as e:
        print(f"Fehler bei der Verbindung zum MQTT Broker: {e}", file=stderr)
        exit(1)

    publish_ha_discovery_config(client)
    reader = Rs500Reader()
    print("Starte Hauptschleife zum Auslesen der Daten...")
    while True:
        sensor_data = reader.get_data()
        if sensor_data:
            print("Daten erfolgreich ausgelesen, publiziere via MQTT...")
            for channel, data in sensor_data.all.items():
                if data:
                    topic = f"rs500/channel_{channel}/state"
                    payload = {"temperature": data.temperature, "humidity": data.humidity}
                    client.publish(topic, json.dumps(payload), retain=True)
                    print(f"  -> Daten für Kanal {channel} an Topic {topic} publiziert.")
        else:
            print("Keine Daten vom Sensor erhalten, versuche es in 60 Sekunden erneut.", file=stderr)
        time.sleep(READ_INTERVAL)
