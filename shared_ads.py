import board
import busio
i2c=busio.I2C(board.SCL,board.SDA)
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn as Channel

ads=ADS.ADS1115(i2c,address=0x49)
ads.gain=1
