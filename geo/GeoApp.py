


MEASUREMENT_PATH="/home/pi/local/measurements/geo"



import os,sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"boot_files"))
from module import Module

from time import sleep, time, strftime
import traceback

from Geophone import Geophone

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"environmental"))
from EnvironmentalApp import EnvironmentalApp




if not os.path.exists(MEASUREMENT_PATH):
    os.makedirs(MEASUREMENT_PATH)


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"commands.txt"),"r") as f:
    HELPTEXT=f.read()


class GeoApp(Module):
    def __init__(self,router,bus):
        super().__init__(router,bus)
        self.bus=bus


        self.geo=Geophone()


    def setup(self):
        self.init()
    def init(self):
        pass

    #for router: give prefix
    def get_id(self):
        return "geo"

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

                duration=10
    
                for term in command[1:]:
                    try:
                        key,value=term.split(":")
                    except:
                        key=term
                        value=""
                    
                    if key in ("d","duration","t","time"):
                        mod=1
                        if value.endswith("m"):
                            mod=60
                            value=value[:-1]
                        elif value.endswith("s"):
                            value=value[:-1]
                            
                        try:
                            duration=int(value)
                        except:
                            self.send_output(self._invalid_command("Invalid duration: '%s'"%value))
                            return
                    else:
                        self.send_output(self._invalid_command("Unknown option '%s'"%key))#unknown key
                        return


                args=[duration]

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
            else:
                if self.check_halt_flag():
                    return False
                sleep(0.0001)
        

    def read(self,args):
        duration=args[0]
        PERIOD=0.002#500Hz

        times=[PERIOD*i for i in range(int(duration/PERIOD))]#list of times at which we nead to measure

        data=[]

        t0=time()+.5# add some for a fair start
        for t in times:
            if self.wait_until(t+t0):
                data.append((time(),self.geo.read()))
            else:
                self.send_output(self._halt())
                break

        #save measurement data on disk
        fname=strftime("%y%m%d%H%M%S") #YYMMDDHHMMSS
        with open(os.path.join(MEASUREMENT_PATH,fname),"w") as file:
            file.write("\n".join(["\t".join([str(t),str(v)]) for t,v in data])) #lines in time<>voltage format
        












     
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
    
    
    env=GeoApp(Router(),bus)
    env.init()
    print("Locomotion app testing environment - enter locomotion commands or 'exit'")
    while True:#(i:=input("> "))!="exit":#walrus operator is python 3.8, pi runs 3.7
        i=input("> ").strip()
        if i=="exit":
            break
        elif i:
            env.execute(i)
