# ELV RS500 to MQTT Bridge - Home Assistant Add-on

![GitHub-Logo](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)

Dieses Add-on für Home Assistant liest die Daten von einer **ELV RS500 Raumklima-Messstation** aus, die per USB angeschlossen ist, und veröffentlicht sie auf einem MQTT-Broker.

Dank der **MQTT Discovery**-Funktion werden alle angeschlossenen Sensoren (bis zu 8 Kanäle mit jeweils Temperatur & Luftfeuchtigkeit) automatisch in Home Assistant als Geräte mit den entsprechenden Entitäten angelegt.

## ✨ Features

* Liest Temperatur- und Luftfeuchtigkeitswerte von bis zu 8 Außensensoren der ELV RS500.
* Veröffentlicht die Daten auf einem MQTT-Broker.
* **Automatische Erkennung (Auto-Discovery)** in Home Assistant: Die Sensoren werden automatisch als 8 separate Geräte (eines pro Kanal) mit jeweils zwei Entitäten (Temperatur und Luftfeuchtigkeit) angelegt.
* Einfache Konfiguration über die Add-on-Oberfläche.

---
## 🙏 Danksagung und Inspiration

Ein großer Teil der Logik zum Auslesen des USB-Geräts und zur Dekodierung der Sensordaten in diesem Projekt basiert auf der hervorragenden Vorarbeit von **Jürgen Rocks**. Sein Projekt [juergen-rocks/raumklima](https://github.com/juergen-rocks/raumklima) war die entscheidende Grundlage hierfür. Vielen Dank!

---
## ⚙️ Installation

1.  Gehe in deiner Home Assistant-Instanz zu **Einstellungen > Add-ons > Add-on Store**.
2.  Klicke oben rechts auf das Menü (drei Punkte) und wähle **Repositories**.
3.  Füge die folgende URL in das Textfeld ein und klicke auf **Hinzufügen**:
    ```
    https://github.com/BobMcCloy/ha-addon-rs5002mqtt
    ```
4.  Scrolle nach unten, bis du das "rs5002mqtt"-Repository siehst, und klicke auf das **rs5002mqtt** Add-on.
5.  Klicke auf **Installieren** und warte, bis die Installation abgeschlossen ist.

---
## 🔧 Konfiguration

Nach der Installation musst du das Add-on konfigurieren, bevor du es starten kannst.

1.  Gehe zum Tab **Konfiguration** im Add-on.
2.  Home Assistant sollte das Feld **`mqtt_host`** bereits automatisch mit `core-mosquitto` ausgefüllt haben, falls du den offiziellen MQTT-Broker verwendest.
3.  Trage den **`mqtt_user`** und das **`mqtt_password`** ein, die du in deinem Mosquitto-Broker für dieses Add-on angelegt hast.
4.  Klicke auf **Speichern**.
5.  Gehe zurück zum **Info**-Tab und starte das Add-on.

Nach dem Start sollten die Geräte und Sensoren automatisch in Home Assistant unter der MQTT-Integration erscheinen.

---
## 🛠️ Funktionsweise

Das Add-on greift direkt auf das USB-HID-Gerät der ELV RS500 Basisstation zu (`VendorID: 0x0483`, `ProductID: 0x5750`). Alle 60 Sekunden wird eine Anfrage an die Station gesendet, um die aktuellen Werte aller 8 Kanäle abzufragen.

Die empfangenen Rohdaten werden dekodiert und anschließend per MQTT veröffentlicht. Für jeden Kanal werden zwei Arten von MQTT-Nachrichten gesendet:

1.  **Discovery-Nachricht:** Eine einmalige Nachricht an `homeassistant/sensor/.../config`, die Home Assistant anweist, das Gerät und die Sensoren zu erstellen.
2.  **Status-Nachricht:** Eine sich wiederholende Nachricht an `rs500/channel_X/state`, die die eigentlichen Messwerte im JSON-Format enthält (z.B. `{"temperature": 21.5, "humidity": 45}`).

---
## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
