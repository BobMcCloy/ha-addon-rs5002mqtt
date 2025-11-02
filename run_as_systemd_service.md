# ELV RS500 to MQTT Bridge - Outside HA

0.  Create MQTT account on the server of your choice
1.  Copy the folder rs5002mqtt to "/opt"
2.  Change the credential examples to the ones created in step 0 in ```/opt/rs5002mqtt/reader.py```
3.  Install these packages and their dependencies
    ```
    sudo apt install python3-hid python3-paho-mqtt
    ```
4.  ```
    sudo ln -s /opt/rs5002mqtt/rs500-mqtt.service /etc/systemd/system/rs500-mqtt.service
    ```
5.  ```
	sudo systemctl daemon-reload
	sudo systemctl start rs500-mqtt
    ```
6.  If there are errors, you can look at it at with
    ```
    journalctl -xeu rs500-mqtt
    ```

