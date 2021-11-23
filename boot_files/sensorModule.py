
import module
import math
import board
import busio
from modules import bme280 as bme
import adafruit_ads1x15.ads1115 as ADS
import time
from adafruit_ads1x15.analog_in import AnalogIn
import traceback

i2c = busio.I2C(board.SCL, board.SDA)


class sensors(module.Module):
#Sensor reading timings in milliseconds
    #Sensor period timing
    bme_period = 500
    geophone_period = 100
    wind_period = 500

    #minimum sampling rate
    # minimumSamplingRate = 100

    #how long the system will be taking readings for. 
    readingTime = 10000 


    def __init__(self):
        self.__ads = ADS.ADS1115(i2c)
        self.__ads.mode = Mode.CONTINUOUS
        self.geo = AnalogIn(self.__ads, ADS.P0) # Geophone analog input
        self.wind = AnalogIn(self.__ads, ADS.P1) # Wind sensor analog input.

        
        
    # General Module setup Commands
    def get_id(self):
        return "sen"

    def help(self):
        text = str(self.get_id()) + " module commands\n"
        return text
    
    def execute(self, command):
        # have the commands running over here
        #prints the command:
        print(command)
        command = command.split()
        if(command[0] == "read"):
            for i in range(1, len(command)):
                subcommand = command[i].split(":")
                bmePeriod, geophonePeriod, windPeriod = None
                if(subcommand[0] == "time"):
                    self.readingTime = int(subcommand[1])
                elif(subcommand[0] == 'bp'):
                    bmePeriod = int(subcommand[1])
                    self.bme_period = bmePeriod
                elif(subcommand[0] == 'gp'):
                    geophonePeriod = int(subcommand[1])
                elif(subcommand[0] == "wp"):
                    windPeriod = int(subcommand[1])
                elif(subcommand[0] == "gain"):
                    self.setGainGeophone(float(subcommand[1]))
            
            # self.setSamplingRate()
            self.readData()
        elif(command[0] == "status"):
            try:
                data = [self.bme_period, self.wind_period, self.geophone_period]
                self.send_to_router(0, "Current Status of sensors", data)
            except:
                self.send_to_router(2, 'Failed to send Message')
    

    def readData(self):
        originalTime = time.time()*1000 # time in milliseconds
        bme_time = originalTime
        geophone_time = originalTime
        wind_time = originalTime

        code = 0
        msg = "Sensor readout"

        bmeCounter = 0
        geophoneCounter = 0
        windCounter = 0
        currentTime = originalTime
        while(currentTime < self.readingTime):
            currentTime = originalTime - time.time()*1000
            bmeData = None
            geoData = None
            windData = None
            try:
                if(currentTime > bmeCounter * bme_time):
                    bmeData = self.readBME280()
                    bmeCounter += bmeCounter
                else:
                    bmeData = None
                if(currentTime > geophoneCounter*geophone_time):
                    geoData = self.readGeophone()
                    geophoneCounter += geophoneCounter
                else:
                    geoData = None
                if(currentTime > windCounter* wind_time):
                    windData = self.readWind()
                    windCounter += windCounter
                else:
                    windData = None


                #Data is in the order Temperature, Humidity, Pressure, Geophone, windData  
                if not bmeData == None:
                    data = [bmeData[0], bmeData[1], bmeData[2], geoData, windData]
                else:
                    #No BME data is available.
                    data = [bmeData, geoData, windData]

                #If any sensor values are missing a warning is sent to the user.     
                if None in data:
                    code = 1
                    msg = "Warning missing data from sensors"
                self.send_to_router(code, msg, data)
            except:
                code= 2
                msg = "Error has occured in the system"
                data = traceback.format_exc
                self.send_to_router(code, msg, data)
                

        
                

    def set_router(self, router):
        return super().set_router()

    def send_to_router(self, code: int, msg: str = None, data=None) -> None:
        return super().send_to_router(code, msg=msg, data=data)

    def check_if_hold(self):
        return super().check_if_hold()
    
    def command_does_not_exist(self, command):
        return super().command_does_not_exist(command)
    
    # Reading commands from BME 280 sensor
    def readBME280(self):
        temperature, pressure, humidity = bme.readBME280All()
        data = [temperature, pressure, humidity]
        return data
    
    def readGeophone(self):
        return [self.geo.value, self.geo.voltage]

    def readWind(self):
        return [self.wind.value, self.wind.voltage]

    def setGainGeophone(self, gain):
        # The gain can be set to the following values:
        # 2/3 = +- 6.144V
        # 1 = +-4.096V
        # 2 = +- 2.048V
        # 4 = +- 1.024V
        # 8 = +- 0.512V
        # 16 = +- 0.256V
        self.__ads.gain = gain

    

if __name__ == "__main__":
    print("Starting sensor read")
    sensors  = Sensors()
    while True:
        command = input()
        try:
            sensors.execute(command)
        except:
            traceback.print_exc()
            
