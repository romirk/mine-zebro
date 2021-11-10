
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

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"boot_file"))
from module import Module



from Lidar import Lidar

import RPi.GPIO as GPIO








with open("commands.txt","r") as f:
    HELPTEXT=f.read()



DEFAULT_DIST_MID=8
DEFAULT_DIST_HALF=10
DEFAULT_DIST_SIDE=12



class LIDARApp:
    def __init__(self,bus,returnfunc,checkhaltfunc):
        #super().__init__(router)

        self.bus=bus
        self.returnf=returnfunc #function for sending back data and errors
        self.checkhalt=checkhaltfunc #function to check halt flag. returns True if the robot should stop

        self.distances=[None]*5#left to right (0=left)
        self.sensors=[Lidar(self.bus,GPIO,i+1) for i in range(5)]

        self.enabled=False

    def setup(self):
        #super().setup()
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
        self.enabled=True
                
    def get_id(self):
        return "lidar"

    def help(self):
        return HELPTEXT

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
            elif command[0]=="on":
                func=self.turn_on
            elif command[0]=="off":
                func=self.turn_off
                
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


    def turn_on(self,args=[]):
        for s in self.sensors:
            sleep(.2)
            try:
                s.enable()
            except:
                s.disable()
                self.returnf(self._error("Turning on LIDAR chip %d failed" % s.num))
        self.returnf(self._data({s.num:{"enabled":s.enabled,"distance":None} for s in self.sensors}))
        self.enabled=True
    
    def turn_off(self,args=[]):
        for s in self.sensors:
            s.disable()
        self.distances=[None]*5
        self.returnf(self._data({s.num:{"enabled":s.enabled,"distance":None} for s in self.sensors}))
        self.enabled=False

    def read(self,args=[]):
        if not self.enabled:
            self.returnf(self._warning("Can't check distances: LIDAR is turned off"))
        
        i=0
        self.distances=[None]*5
        try:
            while i<5:
                self.distances[i]=self.sensors[i].read()
                i+=1
        except:
            self.returnf( self._error("Exception occured while reading sensor %d:\n%s"%(i+1,traceback.format_exc())) )
            return

        self.returnf(self._data({s.num:{"enabled":s.enabled,"distance":self.distances[s.num-1]} for s in self.sensors}))
        return True
    
    def assertsafe(self,args):
        if not self.enabled:
            self.returnf(self._error("Can't check distances: LIDAR is turned off"))
            return

        if not self.read():
            return
        distances=[{False:d,True:0}[d==None] for d in self.distances] #no measurement (None) -> no update

        if None in self.distances:
            self.returnf(self._warning("Not all LIDAR chips are operational"))

        
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
    lidar.setup()
    print("LIDAR app testing environment - enter commands or 'exit'")
    while True:#(i:=input("> "))!="exit":#walrus operator is python 3.8, pi runs 3.7
        i=input("> ").strip()
        if i=="exit":
            break
        if i:
            lidar.execute(i)
