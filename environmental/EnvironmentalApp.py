

MEASUREMENT_PATH="/home/pi/local/measurements/env"



import os,sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"boot_files"))
from module import Module

from time import sleep, time, strftime
import traceback

import bme280 as bme




if not os.path.exists(MEASUREMENT_PATH):
    os.makedirs(MEASUREMENT_PATH)




with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"commands.txt"),"r") as f:
    HELPTEXT=f.read()


class EnvironmentalApp(Module):
    def __init__(self,router,bus):
        super().__init__(router,bus)
        self.bus=bus
        
        self.bme=bme
        bme.setBus(self.bus)


    def setup(self):
        self.init()
    def init(self):
        pass

    #for router: give prefix
    def get_id(self):
        return "env"

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
        #if 1:
            if not len(command):    return self.send_output(self._invalid_command("No command specified"))
            if command[0]=="read": #go dir1:count dir2 dir3
                func=self.read
                args=[]

                if len(command)>1:
                    self.send_output(self._invalid_command("read command takes no parameters"))
                

            elif command[0]=="long":
                func=self.long

                settings=dict(duration=None,interval=None,samples=None)
                
                for term in command[1:]:
                    try:
                        key,value=term.split(":")
                    except:
                        key=term
                        value=""
                    
                    if key in ("d","duration"):
                        mod=1
                        if value.endswith("m"):
                            mod=60
                            value=value[:-1]
                        elif value.endswith("s"):
                            value=value[:-1]
                            
                        try:
                            settings["duration"]=int(value)
                        except:
                            self.send_output(self._invalid_command("Invalid duration: '%s'"%value))
                            return
                        
                        if settings["duration"]<1:
                            self.send_output(self._invalid_command("Invalid duration: '%s'"%value))
                            return
                        
                    elif key in ("i","interval","t","p","period"):
                        mod=1
                        if value.endswith("m"):
                            mod=60
                            value=value[:-1]
                        elif value.endswith("s"):
                            value=value[:-1]
                            
                        try:
                            settings["interval"]=int(value)
                        except:
                            self.send_output(self._invalid_command("Invalid interval: '%s'"%value))
                            return

                        if settings["interval"]<1:
                            self.send_output(self._invalid_command("Invalid interval: '%s'"%value))
                            return
                        
                    elif key in ("s","samples"):
                        try:
                            settings["samples"]=int(value)
                        except:
                            self.send_output(self._invalid_command("Invalid number of samples: '%s'"%value))
                            return

                        if settings["samples"]<2:#need at least 2 (one at start, one at finish)
                            self.send_output(self._invalid_command("Invalid number of samples: '%s'"%value))
                            return
                    else:
                        self.send_output(self._invalid_command("Unknown option '%s'"%key))#unknown key
                        return

                count=sum([int(bool(v)) for v in settings.values()])#no. arguments specified
                if count!=2: #wrong no parameters
                    self.send_output(self._invalid_command("Exactly two parameters must be specified"))
                    return


                args=[settings]

        except:
            self.send_output( self._invalid_command("Exception occured while reading command:\n%s"%traceback.format_exc()) )
            return

        try: #try to execute command. send back traceback if it fails (which might result in a dangerous situation for the rover!)
            func(args)
        except:
            self.send_output( self._error("Exception occured during execution of command:\n%s"%traceback.format_exc()) )
            return


    def wait_until(self,t):#wait until t, while checking halt flag. if halt flag was detected, return False, else return True
        while True:
            delta=t-time()
            if delta<=0:
                return True
            elif delta>=1:
                if self.check_halt_flag():
                    return False
                sleep(1) #go to next second
            else:
                sleep(delta)#get to next measurement position
        

    def long(self,args):
        settings=args[0]

        times=[]#list of times at which we nead to measure

        if settings["duration"]:
            if settings["samples"]:
                settings["interval"]=settings["duration"]/(settings["samples"]-1)
                if settings["interval"]<1:
                    self.send_output(self._warning("Attempting more than one measurement per second!"))
            #duration+interval based
            t=0
            while t<=settings["duration"]:
                times.append(t)
                t+=settings["interval"]
        else: #samples and interval
            times=[settings["interval"]*x for x in range(settings["samples"])]


        data=[]

        t0=time()+.5# add some for a fair start
        for t in times:
            if self.wait_until(t+t0):
                data.append((time(),self.read()))
            else:
                self.send_output(self._halt())
                break

        #save measurement data on disk
        fname=strftime("%y%m%d%H%M%S") #YYMMDDHHMMSS
        with open(os.path.join(MEASUREMENT_PATH,fname),"w") as file:
            file.write("\n".join(["\t".join([str(t)]+[str(v) for v in d]) for t,d in data])) #lines in time<tab>temp<tab>press<tab>hum format
        

    def read(self,args=[]): #take a single measurement

        temperature,pressure,humidity = bme.readBME280All()#flush old measurement
        temperature,pressure,humidity = bme.readBME280All()

        self.send_output(self._data(dict(temperature=temperature,pressure=pressure,humidity=humidity)))

        return temperature,pressure,humidity












     
if __name__=="__main__":
    from pprint import pprint

    from smbus2 import SMBus

    bus=SMBus(1) #create bus


    class Router:
        halt_module_execution=False
        def send_package_to_mcp(self,package,_):
            pprint(package)
    
    
    env=EnvironmentalApp(Router(),bus)
    env.init()
    print("Locomotion app testing environment - enter locomotion commands or 'exit'")
    while True:#(i:=input("> "))!="exit":#walrus operator is python 3.8, pi runs 3.7
        i=input("> ").strip()
        if i=="exit":
            break
        elif i:
            env.execute(i)
