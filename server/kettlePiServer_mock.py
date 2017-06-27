from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
import os

temperature = 25
PUMP_STATUS = False
KETTLE_STATUS = False
temperature_offset = 0


@dispatcher.add_method
def thermowell_temperature():
    global temperature, temperature_offset
    return temperature + int(temperature_offset)


@dispatcher.add_method
def pump_status():
    global PUMP_STATUS
    return PUMP_STATUS


@dispatcher.add_method
def kettle_status():
    global KETTLE_STATUS
    return KETTLE_STATUS


@dispatcher.add_method
def kettle_on():
    global KETTLE_STATUS
    KETTLE_STATUS = True
    return True


@dispatcher.add_method
def kettle_off():
    global KETTLE_STATUS
    KETTLE_STATUS = False
    return True


@dispatcher.add_method
def pump_on():
    global PUMP_STATUS
    PUMP_STATUS = True
    return True


@dispatcher.add_method
def pump_off():
    global PUMP_STATUS
    PUMP_STATUS = False
    return True


@dispatcher.add_method
def temperature_adjust(offset):
    global temperature_offset
    temperature_offset = offset
    return temperature_offset


@Request.application
def application(request):
    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


adjusted_temperature = 0

if __name__ == '__main__':
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
        os.exit(0)
