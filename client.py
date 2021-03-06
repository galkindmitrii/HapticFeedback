"""
A simple client application for a research on Haptics Feedback.
Uses Logical link control and adaptation (L2CAP) Bluetooth protocol.

Features:
- Search for near Bluetooth devices and their capabilities.
- Connect to a discovered device or to a device by provided address.
- Send text or a vibration code to a remote device.
- Training mode which shows final percentage of correct answers.

Requirements:
- PyBluez (http://code.google.com/p/pybluez/)
"""
import os
import sys
import time
import random
import logging
import ConfigParser
from pprint import pprint

import bluetooth


try:
    os.system('cls' if os.name == 'nt' else 'clear')  # clear screen

    # reading bluetooth client settings from file
    config_filename = 'clientconfig.cfg'
    config_section_name = 'BT_client_settings'

    config = ConfigParser.ConfigParser()
    config.read(config_filename)

    PORT = int(config.get(config_section_name, 'port', 0), 16)
    DISCOVERY_DURATION = config.getint(config_section_name,
                                       'discovery_duration')
    FLUSH_CACHE = config.getboolean(config_section_name, 'flush_cache')
    TRAINING_ATTEMPTS = config.getint(config_section_name, 'training_attempts')
    LOG_FILE = config.get(config_section_name, 'log_file')

except ConfigParser.NoSectionError:
    print "\nWarning: Failed to find section '%s' in/or configuration \
file '%s', using default settings." % (config_section_name, config_filename)
    PORT = 0x1001
    DISCOVERY_DURATION = 8
    FLUSH_CACHE = True
    TRAINING_ATTEMPTS = 20
    LOG_FILE = 'client.log'

LOG = logging
LOG.basicConfig(filename=LOG_FILE,
                level=logging.DEBUG,
                format='%(asctime)s - %(levelname)s - %(message)s')


class BlueToothClient(object):
    """
    A class representing bluetooth connectivity and data transfer.
    """
    def __init__(self):
        self.nearby_devices = None
        self.bt_services = None

    def create_bt_socket(self):
        """
        Creates an instance of L2CAP bluetooth socket.
        """
        self.client_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)

    def discover_devices(self):
        """
        Discover visible devices within the DISCOVERY_DURATION time limit.
        1 duration unit equals to 1.28 seconds.
        Setting less than 8 units is not recommended due to possible
        devices undetection.
        """
        print "\nDiscovering all nearby BlueTooth devices...\n"
        self.nearby_devices = bluetooth.discover_devices(
                                                   duration=DISCOVERY_DURATION,
                                                   flush_cache=FLUSH_CACHE,
                                                   lookup_names=True)
        if self.nearby_devices:
            print "Found %d device(-s)" % len(self.nearby_devices)
        else:
            print "No BlueTooth devices around found."

    def nearby_devices_to_dict(self):
        """
        Prints and returns discovered BT devices as a dictionary:
        {Number_of_device: (address, name),}
        """
        nearby_devices_dict = {}
        number = 1
        for device in self.nearby_devices:
            nearby_devices_dict[number] = device
            number += 1

        print "\nRecently discovered BT devices:"
        print "- Num ---- Address --------- Name -"
        pprint(nearby_devices_dict)
        return nearby_devices_dict

    def show_devices(self):
        """
        Shows all recently discovered devices.
        """
        if self.nearby_devices:
            print "List of discovered nearby devices:"
            print "----Name------------Address----"
            for address, name in self.nearby_devices:
                print "  %s - %s" % (name, address)

    def check_address_validity(self, address):
        """
        Checks if given string address valid or not.
        """
        if bluetooth.is_valid_address(address):
            print "Address '%s' is valid." % address
            LOG.debug("Checking address. Address %s is valid." % address)
            return True
        else:
            print "Address '%s' is not valid." % address
            LOG.warning("Checking address. Address %s is NOT valid." % address)

    def find_bt_services(self, name=None, uuid=None, address=None):
        """
        Shows services supported by target device (by name/uuid/address)
        or shows services for all near devices if None is provided.
        """
        print "\nLooking for BlueTooth services...\n"
        if address:
            if not self.check_address_validity(address):
                # should not try to connect if address is not valid
                print "\nExiting..."
                sys.exit(0)

        self.bt_services = bluetooth.find_service(name, uuid, address)

        if self.bt_services:
            for service in self.bt_services:
                print "Service Name: %s" % service["name"]
                print " Host:        %s" % service["host"]
                print " Description: %s" % service["description"]
                print " Provided By: %s" % service["provider"]
                print " Protocol:    %s" % service["protocol"]
                print " Channel/PSM: %s" % service["port"]
                print " Svc classes: %s" % service["service-classes"]
                print " Profiles:    %s" % service["profiles"]
                print " Service ID:  %s" % service["service-id"]
                print "--------------------------------------------"
        else:
            print "No BlueTooth services were found."

    def connect_to_device(self, bt_address):
        """
        Connects to a device with a given BT address and global PORT.
        """
        print "Connecting to a device with \
address %s on port %s ..." % (bt_address, PORT)
        try:
            self.client_socket.connect((bt_address, PORT))
            LOG.debug('Connected to a device with \
address %s on port %s.' % (bt_address, PORT))
            return True
        except bluetooth.btcommon.BluetoothError as exc:
            print "Connection failed: %s." % exc
            LOG.error('Failed to connect, reason:' % exc)
            print "\nWaiting for 5 seconds..."
            # helps if connection was refused due to server being busy
            time.sleep(5)

    def close_connection(self):
        """
        Closes client socket.
        """
        print "\nClosing connection..."
        # workaround with time.sleep to enable
        # full data aquisition by the receiver
        time.sleep(0.2)
        self.client_socket.close()
        print "\nClosed."
        LOG.debug('Current connection was closed.')

    def send_data(self, data):
        """
        Sends given data.
        """
        print "\nSending..."
        self.client_socket.send(data)
        print "\nDone."


class UserMenu(object):
    """
    A class representing interracton with a user.
    """
    def __init__(self):
        self.BTClient = BlueToothClient()
        self.correct_answers = []

    def show_main_menu(self):
        """
        Shows main BT client menu.
        """
        print "\n---------- BlueTooth Client Menu ----------"
        print " (1) Discover all near BlueTooth devices"
        print " (2) Find all near BlueTooth services"
        print " (3) Connect and send data"
        print " (0) Exit"

    def show_connection_menu(self):
        """
        Shows connectivity menu.
        """
        print "\n-------- BlueTooth Connection Menu --------"
        print " (1) Connect to one of the recently discovered device"
        print " (2) Connect to a device with specified BT address"
        print " (3) Start training with a recently discovered device"
        print " (0) Back to the main menu"

    def show_command_menu(self):
        """
        Shows commands menu.
        """
        print "\n-------- BlueTooth Command Menu --------"
        print " (1) Send vibration pattern one"
        print " (2) Send vibration pattern two"
        print " (3) Send vibration pattern three"
        print " (4) Send vibration pattern four"
        print " (5) Send text data"
        print " (0) Close connection and back to main menu"

    def check_user_test_answer(self, answer, correct_answer):
        """
        Appends correct user guesses to a list to count percentage.
        """
        if answer == correct_answer:
            self.correct_answers.append(answer)

    def start_testing_mode(self):
        """
        Sends random vibration and asks user to identify it.
        Shows percentage of correct guesses when finished.
        """
        bt_address_name = self.BTClient.nearby_devices_to_dict()\
          [int(raw_input("\nPlease input target device number: "))]

        print "\nStarting test:"
        for train_attempt in range(TRAINING_ATTEMPTS):
            if self.BTClient.connect_to_device(bt_address_name[0]):
                print "\nAttempt No.", train_attempt + 1
                random_pattern = str(random.randint(1, 4))
                self.process_command_menu_input(random_pattern)
                self.check_user_test_answer(raw_input(
                                       "\nEnter pattern number: "),
                                       random_pattern)
                train_attempt += 1

            self.BTClient.create_bt_socket()

        print "\nCorrect answers: %s percent." % (float(
              len(self.correct_answers)) / TRAINING_ATTEMPTS * 100)
        self.correct_answers = []

    def process_command_menu_input(self, user_input):
        """
        Processes given user commands for data transfer/vibrating patterns.
        """
        if user_input is "0":
            self.BTClient.close_connection()

        elif user_input is "1":
            self.BTClient.send_data("hvc0#_16fd2706")  # pattern 1 code
            self.BTClient.close_connection()

        elif user_input is "2":
            self.BTClient.send_data("hvc0#_6fa459ea")  # pattern 2 code
            self.BTClient.close_connection()

        elif user_input is "3":
            self.BTClient.send_data("hvc0#_a8098c1a")  # pattern 3 code
            self.BTClient.close_connection()

        elif user_input is "4":
            self.BTClient.send_data("hvc0#_886313e1")  # pattern 4 code
            self.BTClient.close_connection()

        elif user_input is "5":
            self.BTClient.send_data(raw_input("\nPlease input text to send: "))
            self.BTClient.close_connection()

    def process_conn_menu_input(self, user_input):
        """
        Processes given user connectivity commands.
        """
        if user_input is "0":
            pass

        elif user_input is "1":
            if self.BTClient.nearby_devices:
                try:
                    bt_address_name = self.BTClient.nearby_devices_to_dict()\
                      [int(raw_input("\nPlease input target device number: "))]
                    if self.BTClient.connect_to_device(bt_address_name[0]):
                        self.show_command_menu()
                        self.process_command_menu_input(raw_input('\nPlease '
                                                            'select option: '))
                except (KeyError, ValueError):
                    print "\nWrong device number."
            else:
                print "No recently discovered nearby devices."

        elif user_input is "2":
            bt_address = raw_input("\nPlease input target device BT address: ")
            if self.BTClient.check_address_validity(bt_address):
                if self.BTClient.connect_to_device(bt_address):
                    self.show_command_menu()
                    self.process_command_menu_input(raw_input('\nPlease '
                                                            'select option: '))

        elif user_input is "3":
            if self.BTClient.nearby_devices:
                try:
                    self.start_testing_mode()
                except (KeyError, ValueError):
                    print "\nWrong device number."
            else:
                print "No recently discovered nearby devices."

    def process_main_menu_input(self, user_input):
        """
        Processes given user choices in the main menu.
        """
        if user_input is "0":
            LOG.info('Haptics Feedback client application closed.')
            sys.exit(0)

        elif user_input is "1":
            self.BTClient.discover_devices()
            self.BTClient.show_devices()

        elif user_input is "2":
            self.BTClient.find_bt_services()

        elif user_input is "3":
            self.show_connection_menu()
            self.process_conn_menu_input(raw_input('\nPlease select option: '))

    def start(self):
        """
        Start interracting with user.
        """
        LOG.info('Haptics Feedback Client application started.')
        while True:
            self.BTClient.create_bt_socket()  # socket can be used only once
            self.show_main_menu()
            self.process_main_menu_input(raw_input('\nPlease select option: '))


if __name__ == '__main__':
    Client = UserMenu()
    Client.start()
