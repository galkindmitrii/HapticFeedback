"""
"""
import os
import sys

import bluetooth


class BlueToothClient(object):
    """
    A class representing bluetooth connectivity and data transfer.
    """
    def __init__(self, port=0x1001):
        self.client_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.port = port

        self.nearby_devices = None
        self.bt_services = None

    def discover_devices(self, discovery_duration=8):
        """
        Discover visible devices within the given time limit.
        1 duration unit equals to 1.28 seconds.
        Setting less than 8 units is not recommended due to possible
        devices undetection.
        """
        print "\nDiscovering all nearby BlueTooth devices...\n"
        self.nearby_devices = None
        self.nearby_devices = bluetooth.discover_devices(
                                                   duration=discovery_duration,
                                                   flush_cache=True,
                                                   lookup_names=True)
        if self.nearby_devices:
            print "Found %d device(-s)" % len(self.nearby_devices)
        else:
            print "No BlueTooth devices around found."

    def nearby_devices_to_dict(self):
        """
        Represents discovered BT devices as a dictionary:
        {Number_of_device: (address, name),}
        """
        if self.nearby_devices:
            nearby_devices_dict = {}
            number = 1
            for device in self.nearby_devices:
                nearby_devices_dict[number] = device
                number += 1
            return nearby_devices_dict
        else:
            return None

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
            print "Address %s is valid." % address
            return True
        else:
            print "Address %s is not valid." % address
            #TODO: Write own exception here
            raise Exception("Bad address")

    def find_bt_services(self, name=None, uuid=None, address=None):
        """
        Shows services supported by target device (by name/uuid/address)
        or shows services for all near devices if None is provided.
        """
        print "\nLooking for BlueTooth services...\n"
        if address:
            self.check_address_validity(address)

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
        Connects to a device with a given BT address and port
        specified during BlueToothClient Class creation.
        """
        print "Connecting to a device with address %s \
        on port %s ..." % (bt_address, self.port)
        self.client_socket.connect((bt_address, self.port))
        print "Connected."

    def close_connection(self):
        """
        Closes client socket.
        """
        print "\nClosing connection..."
        self.client_socket.close()
        print "\nClosed."

    def send_data(self, data):
        """
        Sends given data.
        """
        print "\nSending..."
        self.client_socket.send(data)
        print "\nDone."


class UserMenu(object):
    """
    A class representing interracton with user.
    """
    def __init__(self):
        self.BTClient = BlueToothClient()

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
            nearby_devices = self.BTClient.nearby_devices_to_dict()
            if nearby_devices:
                print "\nRecently discovered BT devices:"
                print "- Number ------ (Address, Name) -"
                print nearby_devices

                bt_address_name = nearby_devices[int(raw_input("\nPlease input"
                " target device number: "))]
                self.BTClient.connect_to_device(bt_address_name[0])
                self.show_command_menu()
                self.process_command_menu_input(raw_input('\nPlease '
                'select option: '))
            else:
                print "No recently discovered nearby devices."

        elif user_input is "2":
            bt_address = raw_input("\nPlease input target device BT address: ")
            self.BTClient.check_address_validity(bt_address)
            self.BTClient.connect_to_device(bt_address)
            self.show_command_menu()
            self.process_command_menu_input(raw_input('\nPlease '
            'select option: '))

    def process_main_menu_input(self, user_input):
        """
        Processes given user choices in the main menu.
        """
        if user_input is "0":
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
        while True:
            self.show_main_menu()
            self.process_main_menu_input(raw_input('\nPlease select option: '))


if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')  # clear screen
    Menu = UserMenu()
    Menu.start()
