import sys
import os
import yaml
from collections import OrderedDict
from kettleClient import KettleClient
import time
import datetime
import sendpush


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


def time_to_add_hops(end):
    global loaded_recipe
    for hop in loaded_recipe['hopschedule']:
        two_sec_pre_hopaddition = datetime.timedelta(seconds=hop['time'] * SECONDS_IN_MINUTE - 2)
        two_sec_after_hopaddition = datetime.timedelta(seconds=hop['time'] * SECONDS_IN_MINUTE + 2)
        if two_sec_pre_hopaddition <= time_left(end) <= two_sec_after_hopaddition:
            hop_msg_title = 'Add hop {}!'.format(hop['name'])
            hop_msg = 'Add hop {} time remaining is {}'.format(hop['name'], time_left(end))
            print(hop_msg)
            sendpush.send_notification(hop_msg_title, hop_msg)
            loaded_recipe['hopschedule'].remove(hop)


def send_push_brewstep(brewstep, message):
    sendpush.send_notification("{}, {}".format(brewstep['name'], message),
                               "current temperature: {}".format(current_temperature))


def heat_to(brewstep, start):
    global current_temperature
    current_temperature = k.thermowell_temperature()
    k.kettle_on()
    send_push_brewstep(brewstep, "Starting to heat")
    while brewstep['temperature'] > current_temperature:
        current_temperature = k.thermowell_temperature()
        print("{} | {} | Heating to {}c Current temp: {}c.".format(
            brewstep['name'], time_running(start), brewstep['temperature'], current_temperature))
        time.sleep(1)
    k.kettle_off()
    send_push_brewstep(brewstep, "Heating done")


def cool_to(brewstep, start):
    global current_temperature
    current_temperature = k.thermowell_temperature()
    k.kettle_off()
    send_push_brewstep(brewstep, "Starting to cool")
    while brewstep['temperature'] < current_temperature:
        current_temperature = k.thermowell_temperature()
        print("{} | {} | Cooling to {}c Current temp: {}c.".format(
            brewstep['name'], time_running(start), brewstep['temperature'], current_temperature))
        time.sleep(1)
    send_push_brewstep(brewstep, "Cooling done")


def prestep_ack(brewstep):
    try:
        if brewstep['ack'].lower() in 'prestep':
            sendpush.send_notification("{}, {}".format(brewstep['name'], brewstep['ack_msg']), brewstep['ack_msg'])
            input('\n\n{}. Press almost any key to continue.\n\n'.format(brewstep['ack_msg']))
    except:
        pass


def poststep_ack(brewstep):
    try:
        if brewstep['ack'].lower() in 'poststep':
            sendpush.send_notification("{}, {}".format(brewstep['name'], brewstep['ack_msg']), brewstep['ack_msg'])
            input('\n\n{}. Press almost any key to continue.\n\n'.format(brewstep['ack_msg']))
    except:
        pass


def start_brewing():
    """Start brewing the recipe."""
    global current_temperature
    k.pump_on()
    current_temperature = k.thermowell_temperature()
    for brewstep in loaded_recipe['brewingsteps']:
        print("\n\n====== BREWSTEP =======\n======  {}  ======\n".format(brewstep['name']))
        start = datetime.datetime.now()
        if brewstep['name'].lower() in 'fermentation':
            print("Cooling to: {}, current temperature: {}".format(brewstep['temperature'], current_temperature))
            cool_to(brewstep, start)
        else:
            print("Heating to: {}, current temperature: {}".format(brewstep['temperature'], current_temperature))
            heat_to(brewstep, start)
        prestep_ack(brewstep)
        start = datetime.datetime.now()
        end = start + datetime.timedelta(seconds=(brewstep['time'] * SECONDS_IN_MINUTE))
        if brewstep['name'].lower() in ['boil']:
            print("Starting brewstep: {}".format(brewstep['name']))
            k.kettle_on()
            while datetime.datetime.now() <= end:
                current_temperature = k.thermowell_temperature()
                print(count_down_message(brewstep['name'], end, current_temperature))
                time_to_add_hops(brewstep=brewstep, end=end)
                time.sleep(1)
        else:
            print("Starting brewstep: {}".format(brewstep['name']))
            while datetime.datetime.now() <= end:
                current_temperature = set_temperature(brewstep['temperature'])
                print(count_down_message(brewstep['name'], end, current_temperature))
                time.sleep(1)
        poststep_ack(brewstep)


def list_recipes():
    """List recipes"""
    choice = None
    menu_message = "Recipes list"
    while choice != 'q':
        clear()
        print("\n " + ("-=" * len(menu_message)), end="-\n\n")
        print((" " * int(len(menu_message) / 2)) + menu_message + (" " * int(len(menu_message) / 2)))
        print("\n " + ("-=" * len(menu_message)), end="-\n\n")
        print("Enter recipe number or 'q' to quit to main menu.\n")
        recipes = os.listdir("recipes")
        for i in recipes:
            print("{}. {}".format(recipes.index(i), i))
        choice = int(input('Load recipe: '))
        load_recipe(recipes[choice])
        print("\n")
        break


def load_recipe(recipe_name):
    """Load recipe"""
    global loaded_recipe
    with open("recipes/{}".format(recipe_name), 'r') as ymlfile:
        loaded_recipe = yaml.load(ymlfile)


def print_recipe_detail(loaded_recipe):
    print("\nRecipe name: {}"
          "\nVersion: {}"
          "\nABV: {}".format(loaded_recipe['recipe']['name'],
                             loaded_recipe['recipe']['version'],
                             loaded_recipe['recipe']['abv']))
    print("\n\n=== Brewingsteps ===")
    for i in loaded_recipe['brewingsteps']:
        print("\nStep name: {}"
              "\nTemperature: {}"
              "\nTime: {} minutes".format(i['name'],
                                          i['temperature'],
                                          i['time']))
    print("\n\n=== Hop Schedule ===")

    for i in loaded_recipe['hopschedule']:
        print("\nStep name: {}"
              "\nTemperature: {}"
              "\nTime: {} minutes".format(i['name'],
                                          i['ammount'],
                                          i['time']))


def recipe_detail():
    """Show recipe details"""
    global loaded_recipe
    if loaded_recipe is None:
        menu_message = "No loaded recipe."
    else:
        menu_message = "Recipe details for: {}".format(loaded_recipe['recipe']['name'])
    decorator = ("-=" * len(menu_message)) + "-\n"
    choice = None
    while choice != 'q':
        clear()
        print(decorator)
        print((" " * int(len(menu_message) / 2)) + menu_message)
        print("\n" + decorator)
        print("Press any key for main menu.\n")
        if loaded_recipe:
            print_recipe_detail(loaded_recipe)
        input('continue')
        break


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
            if choice is '3':
                menu[choice]()
                sys.exit(0)
            else:
                menu[choice]()
        print("\n")


def power_off_kettle():
    k.kettle_off()
    k.pump_off()


menu = OrderedDict([
    ('1', list_recipes),
    ('2', recipe_detail),
    ('3', start_brewing),
])

loaded_recipe = None
current_temperature = None
kettle_is_on = False
adjust_temperature = 0
kettleServer = "http://192.168.0.17:4000/jsonrpc"
k = KettleClient(kettleServer)

if __name__ == "__main__":

    SECONDS_IN_MINUTE = 60
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
