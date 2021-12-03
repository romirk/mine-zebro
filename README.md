# setup
This branch contains information and files to set up the system

# Steps to get the rover working
- Create bootable SD ([Tutorial](https://www.raspberrypi.org/documentation/computers/getting-started.html))
- Create empty ssh file in boot partition to enable ssh

Wifi:
- Create wpa_supplicant.conf file in boot partition ([Tutorial](https://www.raspberrypi-spy.co.uk/2017/04/manually-setting-up-pi-wifi-using-wpa_supplicant-conf/), don't include country or scan)

Usb:
- ???

Basic system stuff:
- `ssh` into pi (pi@raspberrypi.local)
- Change password using `passwd`
- Make sure to note down the password somewhere!
- Update system: `sudo apt update`

Setup file system in /home/pi
- Make folder for locally stored data (such as rover specific settings): `mkdir local`
- Get global data from main github branch (or use download-global.sh):
  - (If it exists) `rm -r global`
  - `wget https://github.com/The-Redstar/mine-zebro/archive/global.zip`
  - `unzip global.zip`
  - `mv mine-rover-global global`
  - `rm global.zip`
  - `cd global`
  - `bash download-global.sh` This will automatically download everything (again) and setup some things

Python3:
- `sudo apt install python3-pip`
- `sudo apt install python3-numpy`

I2C:
- Turn on I2C in `sudo raspi-config` > Interfacing Options > I2C > Enable
- Reboot

[comment]: # (- `sudo apt install python-smbus`???? (I did this, but don't think we need it))
- `sudo apt install i2c-tools` (so we can see connected devices using `sudo i2cdetect -y 1`)
- `pip3 install smbus2`

Lidar:
- `sudo pip3 install vl53l1x`

ADC:
- `sudo pip3 install adafruit-circuitpython-ads1x15`


Camera:
- `sudo apt install python3-opencv`

[comment]: # (- `pip install python3-opencv`)

Communication:
- `pip install flask`
- `pip install flask-socketio`
- `pip install flask-classful`

Hosting Wifi Netowrk:
Follow this documentation to setup the API.
https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-routed-wireless-access-point
