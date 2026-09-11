# Changelog

## 1.1.3
- **FIX**: Availability (`rs500/status` = `online`) und die HA-Discovery-Configs wurden bisher nur einmalig direkt nach dem allerersten MQTT-Connect publiziert. Riss die Verbindung danach kurz ab (Netzwerk-Hänger, Broker-Neustart, Keepalive-Timeout, ...), feuerte der Broker das Last-Will-Testament (`offline`, retained) und **alle 16 Sensor-Entitäten blieben in Home Assistant dauerhaft `unavailable`**, obwohl das Add-on über den automatischen Paho-Reconnect klaglos weiter Daten gelesen und publiziert hat. Sichtbar wurde das erst nach einem manuellen Neustart des Add-ons.
  Availability + Discovery werden jetzt über einen `on_connect`-Callback bei jedem (Re-)Connect neu publiziert, nicht mehr nur beim Erststart.
- **FIX**: Kürzerer Reconnect-Backoff (`reconnect_delay_set(1, 30)`), damit ein Verbindungsabriss schneller behoben wird.

## 1.1.2
- **FIX**: Korrektur des Start-Skripts (`run.sh` Shebang) für die Ausführung in der Python-Basisumgebung.

## 1.1.1
- **FIX**: Home Assistant Konfigurations-Schema (Slug, Map) repariert, sodass das Add-on wieder erkannt wird.
- **FEATURE**: Hybrid-Konfiguration für Python-Skript (unterstützt nun `/data/options.json` und Umgebungsvariablen).

## 1.1.0
- **FEATURE**: Komplette Integration in die Home Assistant Add-on Oberfläche (Optionen-Reiter). Konfiguration per UI!
- **FEATURE**: Eigenständiger Systemd-Dienst (Standalone-Modus ohne HA) wird nun offiziell unterstützt.
- **FEATURE**: Saubereres Python-Logging hinzugefügt.
- **FEATURE**: MQTT Availability (Last Will and Testament) implementiert. Sensoren werden `offline` angezeigt, wenn das Add-on gestoppt wird.
- **FEATURE**: Das Auslese-Intervall ist jetzt dynamisch anpassbar (`read_interval`).
- **FEATURE**: "Graceful Shutdown" eingebaut. Beendet USB und MQTT-Verbindung bei Add-on-Stop sauber.
