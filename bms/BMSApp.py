


BMS_VOLTAGE_DIVISION=0.170
MAX_CELL_VOLTAGE=4.1
MIN_CELL_VOLTAGE=3.2

import os,sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"boot_files"))
from module import Module


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_ads import ads,Channel,ADS


import traceback


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"commands.txt"),"r") as f:
    HELPTEXT=f.read()


class BMSApp(Module):
    def __init__(self,router,bus):
        super().__init__(router,bus)
        self.bus=bus

        self.chan=Channel(ads,ADS.P0)

    def setup(self):
        self.init()
    def init(self):
        pass

    #for router: give prefix
    def get_id(self):
        return "bms"

    #return helptext
    def help(self):
        return super().help()+HELPTEXT

    def get_state(self):
        self.read()

    #function for executing commands
    def execute(self,command):
        command=command.split() #commands consist of terms separated by spaces
        func,args=None,[]

        try: #in case of an error, report back the exact error
            if not len(command):    return self.send_output(self._invalid_command("No command specified"))
            if command[0]=="read": #go dir1:count dir2 dir3
                func=self.read
                args=[]

                if len(command)>1:
                    self.send_output(self._invalid_command("read command takes no parameters"))
            else:
                return self.send_output(self._invalid_command())

        except:
            self.send_output( self._invalid_command("Exception occured while reading command:\n%s"%traceback.format_exc()) )
            return

        try: #try to execute command. send back traceback if it fails (which might result in a dangerous situation for the rover!)
            func(args)
        except:
            self.send_output( self._error("Exception occured during execution of command:\n%s"%traceback.format_exc()) )
            return

    def read(self,args=[]): #take a single measurement

        #read voltage from adc
        x=self.chan.voltage #value automatically read by accessing variable

        voltage=x/BMS_VOLTAGE_DIVISION/ads.gain

        percentage=round(max(0,min(100,100*((voltage-4*MIN_CELL_VOLTAGE)/(4*MAX_CELL_VOLTAGE-4*MIN_CELL_VOLTAGE)))))

        self.send_output(self._data({"percentage":percentage,"voltage":voltage}))








     
if __name__=="__main__":
    from pprint import pprint

    from smbus2 import SMBus

    bus=SMBus(1) #create bus


    class Router:
        halt_module_execution=False
        def send_package_to_mcp(self,package,_):
            pprint(package)
        def check_halt_flag(self):
            return self.halt_module_execution
    
    
    bms=BMSApp(Router(),bus)
    bms.init()
    print("Locomotion app testing environment - enter locomotion commands or 'exit'")
    while True:#(i:=input("> "))!="exit":#walrus operator is python 3.8, pi runs 3.7
        i=input("> ").strip()
        if i=="exit":
            break
        elif i:
            bms.execute(i)
