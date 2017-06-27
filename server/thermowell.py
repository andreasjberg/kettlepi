import os
import glob
import time


class Thermowell:
    def __init__(self):
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        self.base_dir = '/sys/bus/w1/devices/'
        self.device_folder = glob.glob(self.base_dir + '28*')[0]
        self.device_file = self.device_folder + '/w1_slave'

    def read_raw_temperature(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temperature(self):
        lines = self.read_raw_temperature()
        while lines[0].strip()[-3:] == 'YES':
            time.sleep(0.2)
            lines = self.read_raw_temperature()
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos + 2:]
                temp_c = float(temp_string) / 1000.0
                # temp_f = temp_c * 9.0 / 5.0 + 32.0
                return temp_c


if __name__ == '__main__':
    tw = Thermowell()
    while True:
        print(tw.read_temperature())
        time.sleep(1)
