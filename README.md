# ELV RS500 to MQTT Bridge - Home Assistant Add-on

![GitHub-Logo](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)

Dieses Add-on für Home Assistant liest die Daten von einer **ELV RS500 Raumklima-Messstation** aus, die per USB angeschlossen ist, und veröffentlicht sie auf einem MQTT-Broker.

Dank der **MQTT Discovery**-Funktion werden alle angeschlossenen Sensoren (bis zu 8 Kanäle mit jeweils Temperatur & Luftfeuchtigkeit) automatisch in Home Assistant als Geräte mit den entsprechenden Entitäten angelegt.

## ✨ Features

* Liest Temperatur- und Luftfeuchtigkeitswerte von bis zu 8 Außensensoren der ELV RS500.
* Veröffentlicht die Daten auf einem MQTT-Broker.
* **Automatische Erkennung (Auto-Discovery)** in Home Assistant: Die Sensoren werden automatisch als 8 separate Geräte (eines pro Kanal) mit jeweils zwei Entitäten (Temperatur und Luftfeuchtigkeit) angelegt.
* Konfiguration erfolgt über eine einfache JSON-Datei.

---
## 🙏 Danksagung und Inspiration

Ein großer Teil der Logik zum Auslesen des USB-Geräts und zur Dekodierung der Sensordaten in diesem Projekt basiert auf der hervorragenden Vorarbeit von **Jürgen Rocks**. Sein Projekt [juergen-rocks/raumklima](https://github.com/juergen-rocks/raumklima) war die entscheidende Grundlage hierfür. Vielen Dank!

---
## ⚙️ Installation

Um dieses Add-on zu installieren, musst du dieses GitHub-Repository zu deinem Home Assistant Add-on Store hinzufügen.

1.  Gehe in deiner Home Assistant-Instanz zu **Einstellungen > Add-ons > Add-on Store**.
2.  Klicke oben rechts auf das Menü (drei Punkte) und wähle **Repositories**.
3.  Füge die folgende URL in das Textfeld ein und klicke auf **Hinzufügen**:
    ```
    https://github.com/BobMcCloy/ha-addon-rs5002mqtt
    ```
4.  Schließe das Dialogfenster. Das neue Repository erscheint nun am Ende der Add-on-Store-Seite.
5.  Klicke auf das **rs5002mqtt** Add-on, um es zu öffnen.
6.  Klicke auf **Installieren** und warte, bis die Installation abgeschlossen ist.

---
## 🔧 Konfiguration (WICHTIG)

Dieses Add-on wird über eine Konfigurationsdatei eingerichtet, nicht über die normale Konfigurationsoberfläche.

**Schritt 1: Konfigurationsdatei erstellen lassen**

1.  Nach der Installation, starte das Add-on **einmal**. Es wird sofort wieder stoppen. Das ist normal.
2.  Schau in den **Log** des Add-ons. Dort findest du eine Meldung, die dich anweist, die Konfigurationsdatei zu bearbeiten. Dieser erste Start hat die notwendige Datei für dich erstellt.
3.  **Stoppe** das Add-on.

**Schritt 2: Zugangsdaten eintragen**

1.  Öffne den **"File editor"** in Home Assistant (oder greife per Samba auf deine Konfiguration zu).
2.  Navigiere zum Verzeichnis `/data/`. (Im File Editor musst du eventuell auf das Ordner-Symbol oben klicken, um zum Hauptverzeichnis `/` zu gelangen).
3.  Öffne die Datei `mqtt_config.json`, die dort nun liegt. Sie sieht so aus:
    ```json
    {
      "mqtt_host": "core-mosquitto",
      "mqtt_user": "BITTE_AENDERN",
      "mqtt_password": "BITTE_AENDERN"
    }
    ```
4.  Ersetze `"BITTE_AENDERN"` mit deinem MQTT-Benutzernamen und -Passwort. Lasse den `mqtt_host` auf `core-mosquitto`, falls du den offiziellen Home Assistant MQTT Broker nutzt.
5.  **Speichere** die Datei.

**Schritt 3: Add-on final starten**

1.  Gehe zurück zu **Einstellungen > Add-ons > rs5002mqtt**.
2.  Klicke auf **Start**.

Das Add-on wird jetzt deine Zugangsdaten aus der Datei lesen und sich erfolgreich mit dem MQTT-Broker verbinden.

---
## 🛠️ Funktionsweise

Das Add-on greift direkt auf das USB-HID-Gerät der ELV RS500 Basisstation zu (`VendorID: 0x0483`, `ProductID: 0x5750`). Alle 60 Sekunden wird eine Anfrage an die Station gesendet, um die aktuellen Werte aller 8 Kanäle abzufragen.

Die empfangenen Rohdaten werden dekodiert und anschließend per MQTT veröffentlicht. Für jeden Kanal werden zwei Arten von MQTT-Nachrichten gesendet:

1.  **Discovery-Nachricht:** Eine einmalige Nachricht an `homeassistant/sensor/.../config`, die Home Assistant anweist, das Gerät und die Sensoren zu erstellen.
2.  **Status-Nachricht:** Eine sich wiederholende Nachricht an `rs500/channel_X/state`, die die eigentlichen Messwerte im JSON-Format enthält (z.B. `{"temperature": 21.5, "humidity": 45}`).

---
## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
