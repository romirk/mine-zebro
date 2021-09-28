# mine-zebro
System for the mine rover side project of the Lunar Zebro team.

# Steps to get the rover working
- Create bootable SD ([Tutorial](https://www.raspberrypi.org/documentation/computers/getting-started.html))
- Create empty ssh file in boot partition to enable ssh

Wifi:
- Create wpa_supplicant.conf file in boot partition ([Tutorial](https://www.raspberrypi-spy.co.uk/2017/04/manually-setting-up-pi-wifi-using-wpa_supplicant-conf/), don't include country or scan)

Usb:
- ???

- `ssh` into pi (pi@raspberrypi.local)
- Change password using `passwd`
- Update system: `sudo apt update`

- Turn on I2C??? `sudo raspi-config` > Interfacing Options > Advanced > I2C > Enable and reboot
