

import os,sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_ads import ads,Channel,ADS


class Geophone:
    def __init__(self):
        self.chan=Channel(ads,ADS.P2,ADS.P3)
    def read(self):
        x=self.chan.voltage/ads.gain

        return x
