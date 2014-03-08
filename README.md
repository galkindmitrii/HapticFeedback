Haptic Feedback
===============

A Python client-server application for Android for research on Haptics Feedback.
All the data transfer is handled by Bluetooth Logical link control and
adaptation protocol (L2CAP). The server should be a device running Android and
being able to vibrate. Client can be any GNU/Linux based computer with a 
Bluetooth dongle. Both sides are using PyBluez library to communicate via
Bluetooth.

Server features:
- Accept L2CAP connections and process received data.
- Distinguish and vibrate with 4 tactile patterns.
- Receive text data.

Client features:
- Search for near Bluetooth devices and their capabilities.
- Connect to a discovered device or to a device by provided address.
- Send text or a vibration code to connected remote device.
- Training mode which shows final percentage of correct answers.

For more infomation regarding the application and experiment conducted,
check the Haptics Feedback Research.pdf
