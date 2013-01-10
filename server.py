"""
A simple server application for a research on Haptics Feedback.
Uses Logical link control and adaptation (L2CAP) Bluetooth protocol.

Features:
- Accepts L2CAP connections and processes received data.
- If received data is a vibration code: vibrates with the device accordingly.
- Else displays the data.

Requirements:
- Android 2.2+ (Tested on 2.3.5)
- SL4A_r6 (http://code.google.com/p/android-scripting/)
- Python for Android 2.6+ (Availiable for download:
  http://code.google.com/p/android-scripting/downloads/list)
- PyBluez (ARM version 0.19 can be found via link:
  http://code.google.com/p/python-for-android/downloads/list)
"""
import time
import logging
import ConfigParser

import android
import bluetooth


try:
    # reading bluetooth server settings from file
    config_filename = 'serverconfig.cfg'
    config_section_name = 'BT_server_settings'

    config = ConfigParser.ConfigParser()
    config.read(config_filename)

    PORT = int(config.get(config_section_name, 'port', 0), 16)
    SOCKET_TIMEOUT = config.getint(config_section_name, 'socket_timeout')
    LOG_FILE = config.get(config_section_name, 'log_file')

except ConfigParser.NoSectionError:
    print "\nWarning: Failed to find section '%s' in/or configuration \
file '%s', using default settings." % (config_section_name, config_filename)
    PORT = 0x1001
    SOCKET_TIMEOUT = 60
    LOG_FILE = 'server.log'

LOG = logging
LOG.basicConfig(filename=LOG_FILE,
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s')


class VibratingPhone(object):
    """
    A class representing different vibration patterns.

    Design made according to assumption that learning more
    than 6 tactile patterns is not trivial and rarely applicable.
    """
    def __init__(self):
        self.Droid = android.Android()

    def pattern_one(self):
        self.Droid.vibrate(1200)

    def pattern_two(self):
        self.Droid.vibrate(700)
        time.sleep(1.2)
        self.Droid.vibrate(700)

    def pattern_three(self):
        self.Droid.vibrate(250)
        time.sleep(0.4)
        self.Droid.vibrate(250)
        time.sleep(0.4)
        self.Droid.vibrate(250)

    def pattern_four(self):
        for vibration in range(12):
            self.Droid.vibrate(100)
            time.sleep(0.1)
            vibration += 1

    def vibrate(self, data):
        if data == '16fd2706':
            self.Droid.dialogCreateAlert('Message received',
                                         'Vibrating pattern one')
            self.Droid.dialogShow()
            self.pattern_one()

        elif data == '6fa459ea':
            self.Droid.dialogCreateAlert('Message received',
                                         'Vibrating pattern two')
            self.Droid.dialogShow()
            self.pattern_two()

        elif data == 'a8098c1a':
            self.Droid.dialogCreateAlert('Message received',
                                         'Vibrating pattern three')
            self.Droid.dialogShow()
            self.pattern_three()

        elif data == '886313e1':
            self.Droid.dialogCreateAlert('Message received',
                                         'Vibrating pattern four')
            self.Droid.dialogShow()
            self.pattern_four()

        else:
            LOG.debug('No interpretation available for code %s' % data)
            print "\nNon interpretable vibration code..."


class BlueToothServer(object):
    """
    A class representing bluetooth connectivity and data transfer.
    """
    def __init__(self):
        self.VibroPhone = VibratingPhone()
        self.server_socket = None

    def show_server_info(self):
        """
        Shows main info concerning device.
        """
        Name = self.VibroPhone.Droid.bluetoothGetLocalName()
        Address = self.VibroPhone.Droid.bluetoothGetLocalAddress()

        print '\n--- Haptics Feedback Server ---'
        print 'Name:', Name.result
        print 'Address:', Address.result
        print 'Port:', PORT
        print 'Connection timeout:', SOCKET_TIMEOUT, 'sec'
        print 'Log file:', LOG_FILE
        print '-------------------------------'

    def bind_and_receive_data(self):
        """
        Binds to server socket, accepts connection and
        returns received first 1024 bytes of data.

        Data will be received only from connection that
        was activated first, other data is ignored.

        Active connection is closed after
        SOCKET_TIMEOUT if no data was received.
        """
        self.server_socket.bind(("", PORT))

        # this setting ensures that data from one connection will be received
        self.server_socket.listen(1)

        client_socket, address = self.server_socket.accept()
        print "\nAccepted connection from a device with address: ", address[0]

        client_socket.settimeout(SOCKET_TIMEOUT)

        data = None
        try:
            data = client_socket.recv(1024)
            print "\nFinished receiving data."
        except bluetooth.btcommon.BluetoothError as exc:
            # if error occures - ignoring and closing sockets
            LOG.debug('Exception during data transfer: %s' % exc)
            print '\nConnection timeout. Closing...'

        client_socket.close()
        self.server_socket.close()
        print "\nClosed connection from a device with address: ", address[0]
        return data

    def process_data(self, data):
        """
        A method to decide whether received data is a
        correct vibration code or something else.
        """
        if data.startswith('hvc0#_'):
            LOG.info("Received a vibration code: %s" % data)
            self.VibroPhone.vibrate(data[6:])
        else:
            print "Received data: %s is not a vibration code. Ignoring." % data

    def start_server(self):
        """
        A method to wait for incoming BT connections and receive data.
        """
        LOG.info('Haptics Feedback Server application started.')
        self.show_server_info()

        while True:
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)

            print "\nWaiting for incoming BT L2CAP connections..."
            data = self.bind_and_receive_data()
            if data:
                self.process_data(data)


if __name__ == '__main__':
    BTServer = BlueToothServer()
    BTServer.start_server()
