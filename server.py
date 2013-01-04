"""
"""
import time

import android
import bluetooth


class VibratingPhone(object):
    """
    A class representing different vibration patterns.

    Design made according to assumption that learning more
    than 6 tactile patterns is not trivial and rarely applicable.
    """
    def __init__(self):
        self.Droid = android.Android()

    def pattern_one(self):
        self.Droid.vibrate(1000)

    def pattern_two(self):
        self.Droid.vibrate(1000)
        time.sleep(2)
        self.Droid.vibrate(1000)

    def pattern_three(self):
        self.Droid.vibrate(300)
        time.sleep(2)
        self.Droid.vibrate(300)

    def pattern_four(self):
        self.Droid.vibrate(100)

    def vibrate(self, data):
        if data == '16fd2706':
            self.pattern_one()
        elif data == '6fa459ea':
            self.pattern_two()
        elif data == 'a8098c1a':
            self.pattern_three()
        elif data == '886313e1':
            self.pattern_four()
        else:
            print "Non interpretable vibration code..."


class BlueToothServer(object):
    """
    A class representing bluetooth connectivity and data transfer.
    """
    def __init__(self, port=0x1001):
        self.VibroPhone = VibratingPhone()
        self.server_socket = None
        self.port = port

    def process_data(self, data):
        """
        A method to decide whether data is a correct
        vibration code or something other.
        """
        if data.startswith('hvc0#_'):
            print "Received a vibration code: %s" % data
            self.VibroPhone.vibrate(data[6:])
        else:
            print "Received data: %s is not a vibration code. Ignoring." % data

    def start_server(self):
        """
        A method to wait for incoming BT connections and receive data.
        """
        while True:
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)

            print "Waiting for incoming BT L2CAP connections..."
            self.server_socket.bind(("", self.port))
            self.server_socket.listen(1)
            client_socket, address = self.server_socket.accept()
            print "Accepted connection from a device with address: ", address

            data = client_socket.recv(1024)
            print "Finished receiving data."

            client_socket.close()
            self.server_socket.close()
            print "Closed connection from a device with address: ", address
            self.process_data(data)


if __name__ == '__main__':
    BTServer = BlueToothServer()
    BTServer.start_server()
