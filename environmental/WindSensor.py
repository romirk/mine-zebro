

import os,sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_ads import ads,Channel,ADS


class WindSensor:
    def __init__(self):
        self.chan=Channel(ads,ADS.P2)
    def read(self):
        x=self.chan.value

        wind_speed=(x-0.4)/(2.0-0.4)*32.4
        return round(wind_speed,1)
