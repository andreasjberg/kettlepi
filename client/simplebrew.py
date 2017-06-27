import sys
import os

from collections import OrderedDict
from kettleClient import KettleClient
import time
import datetime


def chop_microseconds(delta):
    return delta - datetime.timedelta(microseconds=delta.microseconds)


def time_running(start_time):
    return chop_microseconds(datetime.datetime.now() - start_time)


def time_left(end_time):
    return chop_microseconds(end_time - datetime.datetime.now())


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def count_down_message(name, end, temperature):
    return "{} running for {} current temperature {}c".format(name, time_left(end), temperature)


def set_temperature(param):
    """Set temperature to param."""
    global current_temperature
    try:
        current_temperature = k.thermowell_temperature()
        if param > current_temperature:
            k.kettle_on()
        else:
            k.kettle_off()
    except:
        print("SOMETHIGN WENT WRONG!")
    return current_temperature


def heat_to():
    """Heat to temperature"""
    temperature = int(input("What temperature do you want to heat to? "))
    current_temperature = k.thermowell_temperature()
    k.kettle_on()
    start = datetime.datetime.now()
    while temperature > current_temperature:
        current_temperature = k.thermowell_temperature()
        print("{} | Heating to {}c Current temp: {}c.".format(
            time_running(start), temperature, current_temperature))
        time.sleep(1)
    k.kettle_off()
    print("Heating done!")


def cool_to():
    """Cool down to."""
    global current_temperature
    temperature = int(input("What temperature do you want to cool to? "))
    current_temperature = k.thermowell_temperature()
    k.kettle_off()
    start = datetime.datetime.now()
    while temperature < current_temperature:
        current_temperature = k.thermowell_temperature()
        print(" {} | Cooling to {}c Current temp: {}c.".format(
            time_running(start), temperature, current_temperature))
        time.sleep(1)
    print("Cooling done!")


def run_brewstep():
    """Run brewstep for x minutes y temperature."""
    running_time = int(input("Minutes to run boilstep? "))
    temperature = int(input("What is the target temperature? "))
    offset = int(input("Temperature offset? "))
    start = datetime.datetime.now()
    end = start + datetime.timedelta(seconds=(running_time * 60))
    while datetime.datetime.now() <= end:
        current_temperature = set_temperature(temperature + offset)
        print(count_down_message("Manual brewstep", end, current_temperature))
        time.sleep(1)


def run_boil():
    """Run boil for x minutes"""
    running_time = int(input("Minutes to run boil? "))
    start = datetime.datetime.now()
    end = start + datetime.timedelta(seconds=(running_time * 60))
    k.kettle_on()
    print("Ddn = {}".format(datetime.datetime.now()))
    print("End = {}".format(end))
    while datetime.datetime.now() <= end:
        current_temperature = k.thermowell_temperature()
        print(count_down_message("Manual brewstep", end, current_temperature))
        time.sleep(1)


def menu_loop():
    """Show the menu."""
    choice = None
    menu_message = "Home brew automated Biab system main menu"
    decorator = ("-=" * len(menu_message)) + "-\n"
    while choice != 'q':
        if loaded_recipe is not None:
            recipe_message = ("Currently loaded Recipe: {} ".format(loaded_recipe['recipe']['name']))
        else:
            recipe_message = "No currently loaded recipe"
        print(decorator)
        print((" " * int(len(menu_message) / 2)) + menu_message)
        print(" " * (int(len(decorator) / 2) - int(len(recipe_message) / 2)) + recipe_message)
        print("\n" + decorator)
        print("Enter 'q' to quit.\n")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        choice = input('Action: ').lower().strip()
        if choice in menu:
            menu[choice]()
        print("\n")


def power_off_kettle():
    k.kettle_off()
    k.pump_off()


menu = OrderedDict([
    ('1', heat_to),
    ('2', run_brewstep),
    ('3', run_boil),
])

loaded_recipe = None
current_temperature = None
kettle_is_on = False
adjust_temperature = 0
SECONDS_IN_MINUTE = 1

if __name__ == "__main__":
    ip = input("Enter IP for remote host (127.0.0.1): ") or '127.0.0.1'
    url = "http://{}:4000/jsonrpc".format(ip)
    k = KettleClient(url)
    try:
        power_off_kettle()
        menu_loop()

    except KeyboardInterrupt:
        # here you put any code you want to run before the program
        # exits when you press CTRL+C
        k.kettle_off()
        k.pump_off()
        print("\nKeyboard interrupt!")  # print value of counter

    #    except Exception as e:
    # this catches ALL other exceptions including errors.
    # You won't get any error messages for debugging
    # so only use it once your code is working
    #        print("Other error or exception occurred!")
    #        print(e)

    finally:
        sys.exit(0)
