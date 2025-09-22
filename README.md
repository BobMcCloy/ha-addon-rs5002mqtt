# ELV RS500 to MQTT Bridge - Home Assistant Add-on

![GitHub Logo](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)

This Home Assistant add-on reads data from an **ELV RS500 Room Climate Station** connected via USB and publishes it to an MQTT broker.

Thanks to the **MQTT Discovery** feature, all connected sensors (up to 8 channels, each with temperature & humidity) are automatically created in Home Assistant as devices with their corresponding entities.

## ✨ Features

* Reads temperature and humidity values from up to 8 outdoor sensors for the ELV RS500.
* Publishes the data to an MQTT broker.
* **Automatic Discovery** in Home Assistant: Sensors are automatically created as 8 separate devices (one per channel), each with two entities (temperature and humidity).
* Configuration is handled via a simple JSON file.

---
## 🙏 Acknowledgements and Inspiration

A large part of the logic for reading the USB device and decoding the sensor data in this project is based on the excellent groundwork by **Jürgen Rocks**. His project [juergen-rocks/raumklima](https://github.com/juergen-rocks/raumklima) was the crucial foundation for this add-on. Thank you!

---
## ⚙️ Installation

To install this add-on, you need to add this GitHub repository to your Home Assistant Add-on Store.

1.  In your Home Assistant instance, go to **Settings > Add-ons > Add-on Store**.
2.  Click the menu (three dots) in the top right corner and select **Repositories**.
3.  Paste the following URL into the text box and click **Add**:
    ```
    [https://github.com/BobMcCloy/ha-addon-rs5002mqtt](https://github.com/BobMcCloy/ha-addon-rs5002mqtt)
    ```
4.  Close the dialog. The new repository will now appear at the bottom of the Add-on Store page.
5.  Click on the **rs5002mqtt** add-on to open it.
6.  Click **Install** and wait for the installation to complete.

---
### Configuration

**Important:** This add-on uses a **hardcoded configuration**. There is no configuration via the Home Assistant UI. If you need to change the MQTT credentials, you must edit the `reader.py` file directly.

The relevant section is at the top of the `rs5002mqtt/reader.py` file:

```python
# =================================================================
# HARDCODED CREDENTIALS - CHANGE HERE
# =================================================================
CONFIG_MQTT_HOST = "core-mosquitto"
CONFIG_MQTT_USER = "rs5002mqtt"
CONFIG_MQTT_PASSWORD = "rs5002mqtt"
# =================================================================

After editing the file, you must **rebuild** the add-on for the changes to take effect.

Starting the Add-on
1.  Navigate to the add-on's page.
2.  Click Start. The add-on will connect to the MQTT broker using the credentials specified in the reader.py file.



---
## 🛠️ How it Works

The add-on directly accesses the USB HID device of the ELV RS500 base station (`VendorID: 0x0483`, `ProductID: 0x5750`). Every 60 seconds, a request is sent to the station to query the current values of all 8 channels.

The received raw data is decoded and then published via MQTT. For each channel, two types of MQTT messages are sent:

1.  **Discovery Message:** A one-time message sent to `homeassistant/sensor/.../config` that instructs Home Assistant to create the device and its sensors.
2.  **State Message:** A recurring message sent to `rs500/channel_X/state` that contains the actual sensor readings in JSON format (e.g., `{"temperature": 21.5, "humidity": 45}`).

---
## License

This project is licensed under the MIT License.
