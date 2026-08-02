# Changelog

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
