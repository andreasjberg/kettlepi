
#Kettle Pi
KettlePI is an JsonRPC server that controlls a brewkettle. This is done with Raspberry PI, DS18B20 Thermometer and a keyes funduino module. 
BrewKettle is connected to one of the funduino relays and a pump is connected to another relay. kettlePiServer is run on the Raspberry PI that controlls the brewkettle.
App.py is 


#Install instructions
##Requirements
- All hardware connected correctly
- python 3.5

##Software
Install Python PIP
```bash
$ sudo apt-get install python-pip
```
Install Wiring Pi
```bash
git clone git://git.drogon.net/wiringPi
cd wiringPi/
./make
```
Install Werkzeug
```bash
sudo pip install werkzeug
```
Install JsonRPC
```bash
sudo pip install json-rpc
```
Configure raspberry pi for GPIO

Start by adding the following line to /boot/config.txt
You can edit that file with nano by running sudo nano /boot/config.txt and then
scrolling to the bottom and typing it there
```bash
dtoverlay=w1-gpio
```

reboot and run following commands

sudo modprobe w1-gpio
sudo modprobe w1-therm


## Client

To run client/simplebrew.py on Mac OS

1. Install homebrew www.brew.sh
2. # sudo easy_install virtualenv
3. # brew install python3
4. # virtualenv -p /usr/local/bin/python3 ~/kettlepi_env
5. # source ~/kettlepi_env/bin/activate
6. # cd kettlepi
7. # pip install -r requirements.txt
8. # cd client
9. # python3 simplebrew.py
10. # add ip to server


