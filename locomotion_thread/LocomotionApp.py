

"""
USAGE

initialisation:
    loc=LocomotionApp(bus=I2Cbus, returnfunc=outputfunction, checkhaltfunc=check_halt_flag)
    loc.init()#uses I2C bus

run command:
    loc.execute(commandstring)

get help:
    loc.help()

get prefix:
    loc.get_id()




"""


#Locomotion app to manage all locomotion i2c related commands


# Things the locomotion system should be able to do:
# - move forwards/backwards/turn left/right/stand up/lie down/sit/bow/relax LOC:FBLRUDSZR
# - report back information per leg (position, temperature, active) LOC:I[1][2][3][4][5]
# - individual leg control: relax, go to position (either angle or up/down/touch/liftoff) with direction (fd/bd,closest,closest safe) with certain speed/time LOC:(motors, position[<int>,up/down/touchdown/liftoff], direction[fd/bd/closest], speed[fast/slow/...]/time[number of .02ms intervals/<float>[m]s])(...)
# - turn off specific legs for standard walking modes #LOC:X[123456]
# - changing walking modes? LOC:M...
# - detect legs being stuck and responding by setting the motor to relax
# - report back errors such as stuck legs
#
# - possibly lidar stuff????


#command structure
"""

type:
    go
        direction/dir:
            f/fd/forward/forwards
            b/bd/back/backward/backwards
            l/left
            r/right
            u/up/stand_up
            d/down/lie_down
            s/sit
            z/bow
            r/relax
    set
        list of
            m/motors/l/leg:
                one or more of 123456
            [p/pos/position:]
                <angle>
                u/up
                d/down
                t/touch/touchdown
                l/lift/liftoff
            [s/spd/speed/t/time:]
                <time>s
                <time>ms
                <time> #50hz cycles
                s/slow #calculates time based on angle difference
                m/med/medium
                f/fast
            [d/dir/direction:]
                f/fd/forward/forwards
                b/bd/back/backward/backwards
                c/closest
                s/safe #closest only when not turning backwards a lot
            [r/relax:]
                relax
                lock
            [enable|disable]
                enable|disable #turn off motor control for all movement related steps
    get
        [list of motors:] #defaults to all
            any of 123456
            all
        [list of keywords:]
            state
            pos/position
            temperature/temperature
            enabled
    
possible returns
    success:
        0/succes
        1/error
            message:
                incorrect command
                leg stuck
    data
        per motor
            position
            state #enabled/disabled
            temperature
            relaxed
sending set/go commands will return the new position and state if they changed

possible interface stuff
LOC: go f
LOC: go relax
LOC: set m:12 p:120 d:fd s:fast m:56 relax #multiple motors at once!
LOC: get m:34 temp

"""


from ZebroLeg import ZebroLeg, angle_between, abs_angle_difference
import CPG
from locomotion_constants import *

from time import sleep
import traceback



with open("commands.txt","r") as f:
    HELPTEXT=f.read()


GO_DIRECTIONS=[l.split("/") for l in """\
fd/forward/forwards/f
bd/back/backward/backwards
left/l
right/r
up/stand_up/u
down/lie_down/d
sit/s
bow/z
relax/r""".split("\n")]

class LocomotionApp:
    def __init__(self,bus=bus,returnfunc=print,checkhaltfunc=int):
        self.bus=bus
        self.returnf=returnfunc #function for sending back data and errors
        self.checkhalt=checkhaltfunc #function to check halt flag. returns True if the robot should stop
        

        #create legs
        self.NUMBER_OF_LEGS=6

        self.legs=[ZebroLeg(i, bus, self) for i in range(self.NUMBER_OF_LEGS)]
        self.CPG = CPG.CPG(self.legs)

        self.laststep="custom"


    def init(self):

        for leg in self.legs:
            leg.init()
        
        ####run on startup??
        self.standUp()
        sleep(1.1)  # must be larger than 1, as each leg gets a a 1 sec hardcoded time in standUp function


    #for router: give prefix
    def get_id(self):
        return "loc"

    #return helptext
    def help(self):
        return HELPTEXT



    #function for executing commands
    def execute(self,command):
        command=command.split() #commands consist of terms separated by spaces
        func,args=None,[]

        try: #in case of an error, report back the exact error
        #if 1:
            if not len(command):    return self.returnf(self._invalid_command("No command specified"))
            if command[0]=="go": #go dir1:count dir2 dir3
                func=self.go

                
                for term in command[1:]:
                    try:
                        direction,count=term.split(":")
                    except:
                        direction=term
                        count="1"

                    if direction in ("f","fd","forward","forwards"):
                        dir=STEP_FORWARDS
                    elif direction in ("b","bd","back","backward","backwards"):
                        dir=STEP_BACKWARDS
                    elif direction in ("l","left"):
                        dir=STEP_LEFT
                    elif direction in ("r","right"):
                        dir=STEP_RIGHT
                    elif direction in ("u","up","standup","stand_up"):
                        dir=STEP_UP
                    elif direction in ("d","down","liedown","lie_down"):
                        dir=STEP_DOWN
                    elif direction in ("s","sit"):
                        dir=STEP_SIT
                    elif direction in ("z","bow"):
                        dir=STEP_BOW
                    elif direction in ("r","relax"):
                        dir=STEP_RELAX
                    else:
                        self.returnf( self._invalid_command("Unknown direction: '%s'"%direction) )
                        return
                    
                    try:
                        count=int(count)
                        assert count>=1
                    except:
                        self.returnf( self._invalid_command("Invalid count: '%s'"%count))
                        return
                    
                    args.append((dir,count)) 

            elif command[0]=="set":
                func=self.set

                settings=[]

                setting=None#dict(motors=[],position=None,direction=None,speed=None,time=None,relax=None)

                
                for term in command[1:]:
                    try:
                        key,value=term.split(":")
                    except:
                        key=term
                        value=""
                        
                    if key in ("m","motor","motors","leg","legs","l"): #motor allocation creates new setting
                        setting=dict(motors=[],position=None,direction=None,speed=None,time=None,relax=None,state=None,force=None)
                        settings.append(setting) #same object; changes to setting will affect the dict in settings

                        if value=="all":
                            setting["motors"]=[1,2,3,4,5,6]
                        else:
                            try:
                                setting["motors"]=list(map(int,value))
                                if len(set(setting["motors"]).intersection(set([1,2,3,4,5,6])))!=len(setting["motors"]):
                                    raise Exception
                            except:
                                self.returnf( self._invalid_command("Invalid list of legs: '%s'"%value))
                                return
                        
                    elif setting: #if not setting, 
                        if not(key in ("r","relax","state")) and setting["relax"]:
                            self.returnf( self._invalid_command("Cannot relax and move at the same time") )
                            return
                        
                        if key in ("p","pos","position"): #position
                            if setting["position"]!=None:   return self._invalid_command("Multiple positions given")
                            if value in ("u","up"):
                                setting["position"]=LEG_POS_UP
                            elif value in ("d","down"):
                                setting["position"]=LEG_POS_DOWN
                            elif value in ("t","td","touch","touchdown"):
                                setting["position"]=LEG_POS_TOUCHDOWN
                            elif value in ("l","lo","lift","liftoff"):
                                setting["position"]=LEG_POS_LIFTOFF
                            elif value in ("c","current"):
                                setting["position"]=LEG_POS_CURRENT
                            else:
                                try:
                                    value=int(value)%360
                                except:
                                    self.returnf( self._invalid_command("Invalid position: '%s'"%value) )
                                    return #invalid position
                                else:
                                    setting["position"]=value
                                    
                        elif key in ("d","dir","direction"): #direction
                            if setting["direction"]!=None:
                                self.returnf( self._invalid_command("Multiple directions given") )
                                return

                            if value in ("f","fd","forward","forwards"):
                                setting["direction"]=LEG_DIR_FORWARDS
                            elif value in ("b","bd","back","backward","backwards"):
                                setting["direction"]=LEG_DIR_BACKWARDS
                            elif value in ("cw","clockwise"):
                                setting["direction"]=LEG_DIR_CW
                            elif value in ("ccw","counterclockwise"):
                                setting["direction"]=LEG_DIR_CCW
                            elif value in ("c","closest"):
                                setting["direction"]=LEG_DIR_CLOSEST
                            elif value in ("s","safe","safest"): #closest, but prevent standing up backwards
                                setting["direction"]=LEG_DIR_SAFE
                            else:
                                self.returnf( self._invalid_command("Invalid direction '%s'"%value) )
                                return
                            

                        elif key in ("r","relax"): #relax
                            if any([setting[k]!=None for k in ["position","direction","time","speed","state"]]):    return self._invalid_command("Cannot relax and move/change state at the same time")
                            if setting["relax"]!=None:   return self._invalid_command("Multiple relaxes given")

                            if value:
                                self.returnf( self._invalid_command("Relax takes no values: '%s'"%term) )
                                return
                            setting["relax"]=True

                        elif key in ("force",): #force - neglect leg state(enabled/disabled)
                            if setting["force"]!=None:   return self._invalid_command("Multiple forces given")

                            if value:
                                self.returnf( self._invalid_command("Force takes no values: '%s'"%term))
                                return
                            setting["force"]=True

                        elif key in ("state",): #turn on/off leg control
                            if any([setting[k]!=None for k in ["position","direction","time","speed","relax"]]):
                                self.returnf( self._invalid_command("Cannot change leg state and do other things at the same time") )
                                return
                            if setting["state"]!=None:   return self._invalid_command("Multiple states given")

                            if value in ("enabled","disabled"):
                                setting["state"]=value
                            else:
                                self.returnf(self._invalid_command("Invalid state: '%s'"%value))
                                return
                            
                        elif key in ("s","spd","speed"): #speed
                            if setting["speed"]!=None or setting["time"]!=None:
                                self.returnf( self._invalid_command("Multiple speeds/times given") )
                                return

                            if value in ("f","fast"):
                                setting["speed"]=LEG_SPEED_FAST
                            elif value in ("s","slow"):
                                setting["speed"]=LEG_SPEED_SLOW
                            elif value in ("n","normal"):
                                setting["speed"]=LEG_SPEED_NORMAL
                            else:
                                self.returnf( self._invalid_command("Invalid speed: '%s'"%value) )
                                return
                        
                        elif key in ("t","time"): #time
                            if setting["speed"]!=None or setting["time"]!=None:
                                self.returnf( self._invalid_command("Multiple speeds/times given"))
                                return

                            try:
                                if value.endswith("ms"):
                                    setting["time"]=int(value[:-2])/1000*50
                                elif value.endswith("s"):
                                    setting["time"]=int(value[:-1])*50
                                else:
                                    setting["time"]=int(value) #50Hz frames
                            except:
                                self.returnf( self._invalid_command("Invalid time duration: '%s'"%value) )
                                return

                        else:
                            self.returnf( self._invalid_command("Unknown parameter: '%s'"%term))
                            return
                    else:
                        self.returnf(self._invalid_command("Motors must be first parameter"))#invalid command, must give motors as first parameter
                        return


                for setting in settings: #fill in defaults
                    if all([setting[parameter]==None for parameter in ("state","position","relax")]): #for when you have direction but no speed etc
                        self.returnf(self._invalid_command("No actual change specified"))
                        return
                    if setting["direction"]==None:  setting["direction"]=LEG_DIR_SAFE
                    if setting["speed"]==None and setting["time"]==None:
                        setting["speed"]=LEG_SPEED_NORMAL
                    #state, force have None/False defaults we don't need to change

                if not settings:
                    self.returnf( self._invalid_command("No action specified") )
                    return

                args=settings
                    
            elif command[0]=="get":
                func=self.get

                parameters=dict(temperature=False,position=False,state=False,relaxed=False)
                motors=[]

                for term in command[1:]:
                    try:
                        key,value=term.split(":")
                    except:
                        key=term
                        value=""

                    if term in ("temp","temperature","t"):
                        parameters["temperature"]=True
                    elif term in ("pos","position","p","a","angle"):
                        parameters["position"]=True
                    elif term in ("state","s"):
                        parameters["state"]=True
                    elif term in ("relaxed","r"):
                        parameters["relaxed"]=True
                    elif key in ("m","motor","motors","l","leg","legs"):
                        if motors:
                            self.returnf(self._invalid_command("Can only specify one set of legs"))
                            return
                        
                        if value=="all":
                            motors=[1,2,3,4,5,6]
                        else:
                            motors=list(map(int,value))
                            if len(set(motors).intersection(set([1,2,3,4,5,6])))!=len(motors):
                                self.returnf(self._invalid_command("Invalid list of legs: '%s'"%value))
                                return
                    else:
                        self.returnf( self._invalid_command("Invalid argument: '%s'"%term) )
                        return
                    if value and term in ("temp","temperature","t","pos","position","p","a","angle","state","s","relaxed","r"):
                        self.returnf(self._invalid_command("Parameter takes no value: %s"%term))
                        return

                if not motors:
                    motors=[1,2,3,4,5,6]
                if not any(parameters.values()):
                    for key in parameters.keys():
                        parameters[key]=True
                
                args=[motors,parameters]
            else:
                self.returnf( self._invalid_command("No valid action specified") )
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
        return dict(code=0,msg=msg,data)

    #used for initialisation
    def standUp(self):
        return self.set([dict(motors=[1,2,3,4,5,6],position="down",direction="safe")],newstate="up")

    #high level step commands
    def go(self,args):

        for direction,count in args:
            d=direction
            if direction in (STEP_LEFT,STEP_RIGHT):   d=STEP_TURN
            elif direction in (STEP_FORWARDS,STEP_BACKWARDS):  d=STEP_STRAIGHT

            if d!=self.laststep and d!=STEP_DOWN and d!=STEP_UP and d!=STEP_RELAX: #move legs to neutral standup position when starting the lext move, unless it was standing up anyway, and don't whey lying down or relaxing
                if not self.standUp(): #move legs down
                    self.returnf(self._warning("Error occured while standing up, halting step execution"))
                    return
                sleep(1)
            
            #test for last step direction
            for i in range(count):
                if self.checkhalt():
                    self.returnf(self._halt())
                    return
                
                #test for last step direction
                #increment step count

                #generate command pattern
                instructions=self.CPG.create_step(direction)
                

                if not self.set(instructions,newstate=d): #execute, if it fails, stop and return
                    self.returnf(self._warning("Error occured, halting step execution"))
                    return
                self.laststep=d
                

        #use CPG or self.set? last one might be the best tbh
        
        #pprint(args)

    #low level leg commands
    def set(self,args,newstate="custom"):
        #fill in all missing parameters using defaults
        defaults=dict(motors=[],position=None,direction="safe",speed=None,time=None,relax=None,state=None,force=None)
        for setting in args:
            for key,value in defaults.items():
                setting.setdefault(key,value)

        
        #check all relevant motors for temperature and overflow etc.
        halt=False
        for s in args:
            for m in s["motors"]:
                #check motor temperature
                self.legs[m-1].readTemperature()
                #if it is too hot and force is not specified, halt execution, send back error with motor data
                if self.legs[m-1].isOverheated():
                    if s["force"]:
                        self.returnf(self._warning("Forcing overheated leg %d"%m))#send back warning when forced
                    else:
                        if self.legs[m-1].enabled: #disabled legs are neglected
                            halt=True
                            self.returnf(self._error("Leg %d overheated"%m)) #send back error
                    
        if halt:    return

        moving_motors=set()
        #actually execute
        for s in args: #s is one set of motor settings
            #timing stuff?
            if s["state"]:
                for m in s["motors"]:
                    if s["state"]=="enabled":
                        self.legs[m-1].enable()
                    else:
                        self.legs[m-1].disable()
            elif s["relax"]:
                for m in s["motors"]:
                    self.legs[m-1].relax()
            else: #actual /movement/
                #get current position
                angles=[self.legs[m-1].readAngle() for m in s["motors"]]

                moving_motors.update(s["motors"])
                
                #note down start time? should the legs do this themselves?
                
                for m in s["motors"]:
                    self.legs[m-1].smartCommand(position=s["position"],direction=s["direction"],time=s["time"],speed=s["speed"],force=s["force"])

        moving_motors=list(moving_motors)

        #wait some time so that everything has started properly
        sleep(0.1)
        
        
        #wait for legs to complete
        err=False
        done=False
        t=5 #for sleep .1
        while not done:
            done=True #mark true unless a leg is found that isn't ready yet
            for m in moving_motors:
                #read position
                if not self.legs[m-1].isDone():
                    self.legs[m-1].readAngle() #don't look at legs that have finished
                
                #check if leg has finished moving
                if not self.legs[m-1].isDone():
                    done=False #still busy

                    #Check if legs are stuck using time
                    #if they get stuck: relax and disable them, set laststep to custom, continue waiting for other legs
                    #if an error occured, reversed
                    if self.legs[m-1].isStuck(t):
                        err=True
                        self.legs[m-1].relax()
                        self.legs[m-1].disable()
                        self.returnf(self._error("Leg %d stuck; relaxed and disabled leg"%m))

                        self.laststep="custom" #stuck leg means we have an nonstandard leg position
                    
                    
                
            t+=1 #update time
            sleep(0.02)#total delay will be slightly worse but that's ok

        #get new information on legs now that motions have ended, about all relevant motors
        self.get([sum([list(setting["motors"]) for setting in args],[]),dict(position=True,temperature=True,state=True,relaxed=True)])

        if err: #leg got stuck
            return

        #if a leg gets stuck, laststep should be set to custom either way
        self.laststep=newstate
        
        #pprint(args)
        return True #success, needed for step function

    #get leg data without changing anything
    def get(self,args):
        motors,parameters=args

        out={}#output in motor:data format

        #read data from motors
        for m in motors:
            out[m]={}
            if parameters["temperature"]:
                out[m]["temperature"]=self.legs[m-1].readTemperature()
            if parameters["position"]:
                out[m]["position"]=self.legs[m-1].readAngle()
            if parameters["state"]:
                out[m]["state"]={True:"enabled",False:"disabled"}[self.legs[m-1].enabled]
            if parameters["relaxed"]:
                out[m]["relaxed"]=self.legs[m-1].relaxed

        self.returnf(self._data(out))
        
        #pprint(args)





"""
Steps to executing a set of motor commands

-check temperatures for all relevant legs across all command set
    if temperature is outside range: relax and disable leg
    return error
-check positions
-for all legs that need to move: send proper commands
-wait untill all legs are in position:
    keep reading angles
    if leg is still not done after well past the desired time:
        mark leg as stuck
        relax leg
        disable leg
        send error/stack error
        (disabled always count as done)
-report back new positions





"""













     
if __name__=="__main__":
    from pprint import pprint

    from smbus2 import SMBus

    bus=SMBus(1) #create bus
    
    
    loc=LocomotionApp(bus,pprint,int)
    loc.init()
    print("Locomotion app testing environment - enter locomotion commands or 'exit'")
    while True:#(i:=input("> "))!="exit":#walrus operator is python 3.8, pi runs 3.7
        i=input("> ").strip()
        if i=="exit":
            break
        if i:
            loc.execute(i)
