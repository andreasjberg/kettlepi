import sys

import requests
import json
from collections import OrderedDict


class KettleClient:
    def __init__(self, url="localhost:4000/jsonrpc"):
        self.url = url
        self.headers = {'content-type': 'application/json'}

    def post_request(self, payload):
        try:
            response = requests.post(self.url, data=json.dumps(payload), headers=self.headers).json()
        except requests.exceptions.Timeout:
            pass
            # Maybe set up for a retry, or continue in a retry loop
        except requests.exceptions.TooManyRedirects:
            return "Bad URL"
            # Tell the user their URL was bad and try a different one
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            print(e)
            sys.exit(1)
        else:
            return response['result']

    def thermowell_temperature_adjust(self, offset):
        """Adjust temperature"""
        payload = {
            "method": "temperature_adjust",
            "jsonrpc": "2.0",
            "params": [offset],
            "id": 1
        }
        return self.post_request(payload)

    def thermowell_temperature(self):
        """Get Thermowell temperature."""
        payload = {
            "method": "thermowell_temperature",
            "jsonrpc": "2.0",
            "id": 1
        }
        return self.post_request(payload)

    def kettle_status(self):
        """Get kettle status."""
        payload = {
            "method": "kettle_status",
            "jsonrpc": "2.0",
            "id": 2
        }
        return self.post_request(payload)

    def pump_status(self):
        """Get pump status."""
        payload = {
            "method": "pump_status",
            "jsonrpc": "2.0",
            "id": 2
        }
        return self.post_request(payload)

    def kettle_on(self):
        """Turn on kettle."""
        payload = {
            "method": "kettle_on",
            "jsonrpc": "2.0",
            "id": 4
        }
        return self.post_request(payload)

    def kettle_off(self):
        """Turn off kettle."""
        payload = {
            "method": "kettle_off",
            "jsonrpc": "2.0",
            "id": 3
        }
        return self.post_request(payload)

    def pump_on(self):
        """Turn on pump."""
        payload = {
            "method": "pump_on",
            "jsonrpc": "2.0",
            "id": 6
        }
        return self.post_request(payload)

    def pump_off(self):
        """Turn off pump."""
        payload = {
            "method": "pump_off",
            "jsonrpc": "2.0",
            "id": 5
        }
        return self.post_request(payload)


def menu_loop():
    """Show the menu."""
    global temperature_offset, current_temperature, pump_status, kettle_status
    choice = None
    menu_message = "Home brew automated Manual system control."
    decorator = ("-=" * len(menu_message)) + "-\n"
    while choice != 'q':
        print(decorator)
        print((" " * int(len(menu_message) / 2)) + menu_message)
        print("\n\tTemperature = {}, Temperature offset = {}, Kettle: {}, Pump: {}".format(current_temperature,
                                                                                           temperature_offset,
                                                                                           kettle_status,
                                                                                           pump_status))
        print("\n" + decorator)
        print("Enter 'q' to quit.\n")
        for key, value in menu_items.items():
            print('{}) {}'.format(key, value.__doc__))
        choice = input('Action: ').lower().strip()
        if choice in menu_items:
            if choice in ['5']:
                offset = input('Temperature adjustment: ')
                temperature_offset = k.thermowell_temperature_adjust(offset=offset)
            else:
                menu_items[choice]()
        kettle_status = k.kettle_status()
        pump_status = k.pump_status()
        current_temperature = k.thermowell_temperature()
        print("\n")


temperature_offset = 0
current_temperature = 0
pump_status = False
kettle_status = True

if __name__ == "__main__":
    ip = input("Enter IP for remote host (127.0.0.1): ") or '127.0.0.1'
    url = "http://{}:4000/jsonrpc".format(ip)
    k = KettleClient(url)

    menu_items = OrderedDict([
        ('1', k.kettle_on),
        ('2', k.kettle_off),
        ('3', k.pump_on),
        ('4', k.pump_off),
        ('5', k.thermowell_temperature_adjust)
    ])

    menu_loop()
