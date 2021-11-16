import RPi.GPIO
import board
import busio
import modules.bme280 as bme
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class Sensors:

    def __init__(self) -> None:
        pass

    def readBME280(self):
<<<<<<< Updated upstream
        temperature, pressure, humidity = bme.readBME280All()
=======
        temperature, pressure, humidity = bme.readBME280All();
>>>>>>> Stashed changes
        data =[temperature, pressure, humidity]
        return data

    def readAllSensors():
        data = []
        data.append(Sensors.readBME280())
    
    


sensors = Sensors()
print(sensors.readAllSensors())

