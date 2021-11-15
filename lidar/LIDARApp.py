
"""

LIDAR App


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

import os,sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"boot_files"))
from module import Module



from Lidar import Lidar

import RPi.GPIO as GPIO








with open("commands.txt","r") as f:
    HELPTEXT=f.read()



DEFAULT_DIST_MID=8
DEFAULT_DIST_HALF=10
DEFAULT_DIST_SIDE=12



class LIDARApp(Module):

    def get_id(self):
        return "lidar"

    def help(self):
        return super().help()+HELPTEXT


    def __init__(self,router,bus):
        super().__init__(router,bus)

        self.bus=bus

        self.distances=[None]*5#left to right (0=left)
        self.sensors=[Lidar(self.bus,GPIO,i+1) for i in range(5)]

        self.enabled=False

    def setup(self):
        self.init()
    def init(self):
        #super().init()
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
                
    def get_state(self):
        if not self.enabled:
            self.send_output(self._data({s.num:{"enabled":s.enabled,"distance":None} for s in self.sensors}))
        else:
            self.execute("read")

    #function for executing commands
    def execute(self,command):
        command=command.split() #commands consist of terms separated by spaces
        func,args=None,[]

        try: #in case of an error, report back the exact error
            if not len(command):    return self.send_output(self._invalid_command("No command specified"))
            if command[0]=="read": #read values and report back
                if len(command)>1:
                    return self.send_output(self._invalid_command("Command 'read' takes no arguments"))
                func=self.read
                args=[]

            elif command[0]=="assertsafe":
                func=self.assertsafe
                args=[DEFAULT_DIST_MID,DEFAULT_DIST_HALF,DEFAULT_DIST_SIDE]
                for term in command[1:]:
                    try:
                        key,val=term.split(":")
                    except:
                        self.send_output(self._invalid_command("Invalid argument: '%s'"%term))
                        return
                    
                    try:
                        val=int(val)
                        assert val>0
                    except:
                        self.send_output(self._invalid_command("Invalid distance: '%s'"%str(val)))
                        return

                    if key in ("m","mid","middle","c","centre","center"):
                        args[0]=val
                    elif key in ("h","half","halfway"):
                        args[1]=val
                    elif key in ("s","side","o","out","outer"):
                        args[2]=val
                    else:
                        self.send_output(self._invalid_command("Invalid direction: '%s'"%key))
                        return
            elif command[0]=="on":
                func=self.turn_on
            elif command[0]=="off":
                func=self.turn_off
                
            else:
                self.send_output( self._invalid_command("No valid command specified") )
                return

        except:
            self.send_output( self._invalid_command("Exception occured while reading command:\n%s"%traceback.format_exc()) )
            return

        try: #try to execute command. send back traceback if it fails (which might result in a dangerous situation for the rover!)
            func(args)
        except:
            self.send_output( self._error("Exception occured during execution of command:\n%s"%traceback.format_exc()) )
            return

    def turn_on(self,args=[]):
        for s in self.sensors:
            sleep(.2)
            try:
                s.enable()
            except:
                s.disable()
                self.send_output(self._error("Turning on LIDAR chip %d failed" % s.num))
        self.send_output(self._data({s.num:{"enabled":s.enabled,"distance":None} for s in self.sensors}))
        self.enabled=True
    
    def turn_off(self,args=[]):
        for s in self.sensors:
            s.disable()
        self.distances=[None]*5
        self.send_output(self._data({s.num:{"enabled":s.enabled,"distance":None} for s in self.sensors}))
        self.enabled=False

    def read(self,args=[]):
        if not self.enabled:
            self.send_output(self._warning("Can't check distances: LIDAR is turned off"))
        
        i=0
        self.distances=[None]*5
        try:
            while i<5:
                self.distances[i]=self.sensors[i].read()
                i+=1
        except:
            self.send_output( self._error("Exception occured while reading sensor %d:\n%s"%(i+1,traceback.format_exc())) )
            return

        self.send_output(self._data({s.num:{"enabled":s.enabled,"distance":self.distances[s.num-1]} for s in self.sensors}))
        return True
    
    def assertsafe(self,args):
        if not self.enabled:
            self.send_output(self._error("Can't check distances: LIDAR is turned off"))
            return

        if not self.read():
            return
        distances=[{False:d,True:0}[d==None] for d in self.distances] #no measurement (None) -> no update

        if None in self.distances:
            self.send_output(self._warning("Not all LIDAR chips are operational"))

        
        #args in cm -> *10 to mm
        if any([0<distances[i]<10*args[abs(2-i)] for i in range(5)]):#0<self.distances[2]<args[0] or min(self.distances[1::2])<args[1] or min(self.distances[0::4])<args[2]:
            self.send_output(self._error("Object detected within close range"))
            return
        self.send_output(self._info("No object detected within close range"))


     
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
