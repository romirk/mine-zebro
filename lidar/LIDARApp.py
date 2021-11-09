
"""

LIDAR App (might use I2C idk



commands

read
    read values
assertsafe
    read values and check
assertsafe m/mid/middle:<distance> h/half/halfway:<distance> s/side:<distance>
    like assertsafe but with values

"""


from time import sleep
import traceback

from Lidar import Lidar

import RPi.GPIO as GPIO



DEFAULT_DIST_MID=17
DEFAULT_DIST_HALF=20
DEFAULT_DIST_SIDE=20



class LIDARApp:
    def __init__(self,bus,returnfunc,checkhaltfunc):
        self.bus=bus
        self.returnf=returnfunc #function for sending back data and errors
        self.checkhalt=checkhaltfunc #function to check halt flag. returns True if the robot should stop

        self.distances=[0,0,0,0,0]#left to right (0=left)
        self.sensors=[Lidar(self.bus,GPIO,i+1) for i in range(5)]

    def init(self):
        GPIO.setmode(GPIO.BCM)
        for s in self.sensors:
            s.disable()

        for s in self.sensors:
            sleep(.2)
            try:
                s.init()
            except:
                s.disable()
                print("Loading LIDAR chip %d failed" % (self.sensors.index(s)+1))
                
    def get_id(self):
        return "ldr"
    def help(self):
        return "No help implemented"

    #function for executing commands
    def execute(self,command):
        command=command.split() #commands consist of terms separated by spaces
        func,args=None,[]

        try: #in case of an error, report back the exact error
            if not len(command):    return self.returnf(self._invalid_command("No command specified"))
            if command[0]=="read": #read values and report back
                if len(command)>1:
                    return self.returnf(self._invalid_command("Command 'read' takes no arguments"))
                func=self.read
                args=[]

            elif command[0]=="assertsafe":
                func=self.assertsafe
                args=[DEFAULT_DIST_MID,DEFAULT_DIST_HALF,DEFAULT_DIST_SIDE]
                for term in command[1:]:
                    try:
                        key,val=term.split(":")
                    except:
                        self.returnf(self._invalid_command("Invalid argument: '%s'"%term))
                        return
                    
                    try:
                        val=int(val)
                        assert val>0
                    except:
                        self.returnf(self._invalid_command("Invalid distance: '%s'"%str(val)))
                        return

                    if key in ("m","mid","middle","c","centre","center"):
                        args[0]=val
                    elif key in ("h","half","halfway"):
                        args[1]=val
                    elif key in ("s","side","o","out","outer"):
                        args[2]=val
                    else:
                        self.returnf(self._invalid_command("Invalid direction: '%s'"%key))
                        return 
                
            else:
                self.returnf( self._invalid_command("No valid command specified") )
                return

        except:
            self.returnf( self._invalid_command("Exception occured while reading command:\n%s"%traceback.format_exc()) )
            return

        try: #try to execute command. send back traceback if it fails (which might result in a dangerous situation for the rover!)
            func(args)
        except:
            self.returnf( self._error("Exception occured during execution of command:\n%s"%traceback.format_exc()) )
            return

    #some functions for reoccuring results
    def _halt(self):
        return self._error("Execution halted by TRON")
    def _invalid_command(self,err=""):
        if err:
            return self._error("Invalid command: %s"%err)
        return self._error("Invalid command")
    
    def _error(self,err,data={}):
        if data:
            return dict(code=2,msg=err,data=data)
        else:
            return dict(code=2,msg=err)
    def _warning(self,err,data={}):
        if data:
            return dict(code=1,msg=err,data=data)
        else:
            return dict(code=1,msg=err)
    def _data(self,data,msg="Sent data"):
        return dict(code=0,msg=msg,data=data)
    def _info(self,msg):
        return dict(code=0,msg=msg)

    def read(self,args):
        self.distances=[s.read() for s in self.sensors]
        self.returnf(self._data(dict(zip([1,2,3,4,5],self.distances))))
    
    def assertsafe(self,args):
        self.read()
        distances=[{False:d,True:0}[d==None] for d in self.distances] #no measurement (None) -> no update
        
        #args in cm -> *10 to mm
        if any([0<distances[i]<10*args[abs(2-i)] for i in range(5)]):#0<self.distances[2]<args[0] or min(self.distances[1::2])<args[1] or min(self.distances[0::4])<args[2]:
            self.returnf(self._error("Object detected within close range"))
            return
        self.returnf(self._info("No object detected within close range"))


     
if __name__=="__main__":
    from pprint import pprint

    from smbus2 import SMBus

    bus=SMBus(1) #create bus
    
    
    lidar=LIDARApp(bus,pprint,int)
    lidar.init()
    print("LIDAR app testing environment - enter commands or 'exit'")
    while True:#(i:=input("> "))!="exit":#walrus operator is python 3.8, pi runs 3.7
        i=input("> ").strip()
        if i=="exit":
            break
        if i:
            lidar.execute(i)
