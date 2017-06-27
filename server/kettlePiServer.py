from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
import RPi.GPIO as GPIO
from thermowell import Thermowell


KETTLE_GPIO = 17
PUMP_GPIO = 23
temperature_offset = 0

# GPIO setup, Kettle on GPIO17(pin 11), Pump on GPIO23(pin 16)
# Ground on pin 6, VCC on pin 4
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(True)
GPIO.setup(KETTLE_GPIO, GPIO.OUT)
GPIO.setup(PUMP_GPIO, GPIO.OUT)
GPIO.output(PUMP_GPIO, GPIO.LOW)
GPIO.output(KETTLE_GPIO, GPIO.LOW)


# Thermometer DS18B20 at GPIO4 (pin 7), GND on (pin 9), 3,3voltage on pin 1
# This is controlled from temperature.py

@dispatcher.add_method
def temperature_adjust(offset):
    global temperature_offset
    temperature_offset = int(offset)
    return temperature_offset


@dispatcher.add_method
def thermowell_temperature():
    global temperature_offset
    return tw.read_temperature() + temperature_offset


@dispatcher.add_method
def pump_status():
    if GPIO.input(PUMP_GPIO) is 1:
        return True
    else:
        return False


@dispatcher.add_method
def kettle_status():
    if GPIO.input(KETTLE_GPIO) is 1:
        return True
    else:
        return False


@dispatcher.add_method
def kettle_on():
    GPIO.output(KETTLE_GPIO, GPIO.HIGH)
    if kettle_status():
        return True
    else:
        return False


@dispatcher.add_method
def kettle_off():
    GPIO.output(KETTLE_GPIO, GPIO.LOW)
    if kettle_status():
        return False
    else:
        return True


@dispatcher.add_method
def pump_on():
    GPIO.output(PUMP_GPIO, GPIO.HIGH)
    if pump_status():
        return True
    else:
        return False


@dispatcher.add_method
def pump_off():
    GPIO.output(PUMP_GPIO, GPIO.LOW)
    if pump_status():
        return False
    else:
        return True


@Request.application
def application(request):
    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    tw = Thermowell()
    try:
        run_simple('0.0.0.0', 4000, application)

    except KeyboardInterrupt:
        # here you put any code you want to run before the program   
        # exits when you press CTRL+C  
        print("CTRL + C pressed. Exiting")

    # except:  
    #     # this catches ALL other exceptions including errors.  
    #     # You won't get any error messages for debugging  
    #     # so only use it once your code is working  
    #     print "Other error or exception occurred!"  

    finally:
        GPIO.cleanup()  # this ensures a clean exit
