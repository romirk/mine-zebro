from math import floor
from time import sleep

from locomotion_constants import *


DEBUG=True


#test if angle is within some range
def angle_between(x,a,b): #assert a<=b
    while x>b:  x-=360 #ensure x is minimal
    while x<a:  x+=360 #ensure a<=a
    return x<=b #test if a<x<b

#mostly meant for checking of centered range
def abs_angle_difference(a,b):
    return abs(angle_difference(a,b)) #convert difference to [-180,180] interval

def angle_difference(a,b): #a-b
    return (a-b+180)%360-180

class ZebroLeg:
    def __init__(self, leg_num, bus, master):
        self.leg_num = leg_num+1 #own num is 1-based, init thing is 0-based
        self.address = self._address()
        self.bus=bus
        self.master=master

        #i2c addresses
        self.TEMPERATURE_L_ADDRESS = 0x41
        # self.TEMPERATURE_H_ADDRESS = 0x42
        self.LEG_POSITION_ADDRESS = 0x40
        self.DIRECTION_ADDRESS = 0x20
        self.POSITION_ADDRESS = 0x21
        self.TIME_ADDRESS = 0x22

        #named angles
        self.LIEDOWN_ANGLE = 330
        self.STANDUP_ANGLE = 150
        self.TOUCHDOWN_ANGLE = 125
        self.LIFTOFF_ANGLE = 160

        self.SAFE_ANGLE_A=200 #within this range, the leg should avoid turning backwards because that could require immense torque
        self.SAFE_ANGLE_B=300

        #speeds (degrees/50Hz tick)
        self.SPEED_MAX=7.2#round in 1sec
        self.SPEED_MIN=2#fully round in 3.6s
        self.SPEED_FAST=7
        self.SPEED_NORMAL=5
        self.SPEED_SLOW=3#some arbitrary value?



        #correction angles - multiples of 3 are preferred because they correspond to whole position changes, making them consistent
        self.DELTA_ANGLE = 6 #leeway
        self.DELTA_RIGHT = 6 #correction for right leg

        #timing        
        self.TIME_DIVISOR = 0.02 #50Hz timing

        #leg side
        if self.leg_num % 2 == 0:
            self.legSide = "right"
            self.DELTA_SIDE=self.DELTA_RIGHT
        else:
            self.legSide = "left"
            self.DELTA_SIDE=0

        #position
        self.current_angle = self.target_angle = self.readAngle()

        #temperature
        self.MAX_TEMP=45
        self.RESTART_TEMP=35
        self.temperature=25
        self.overheated=False

        #relaxation
        self.relaxed=False

        #state
        self.enabled=True
        self.forced=False #state override

        #variables for leg stuck detection
        self.prev_angle=self.current_angle
        self.progress=0
        self.delta_time=1
        self.direction="f"
        self.LEG_STUCK_DELAY=30#3/5s #fixed allowed delay
        self.LEG_STUCK_FACTOR=1.5 #scalor for progress/speed (i.e. 2 means it will be marked stuck if the leg moves slower than half speed)

    #pick right i2c address
    def _address(self):
        leg_address = {
            1: 0x48,
            2: 0x58,
            3: 0x68,
            4: 0x78,
            5: 0x28,
            6: 0x38
        }[self.leg_num]
        return leg_address


    #read leg position
    def readAngle(self):
        self.current_angle = self.bus.read_byte_data(self.address, self.LEG_POSITION_ADDRESS) * 3 #request angle and convert to degrees

        self.current_angle-=self.DELTA_SIDE #correction for right side legs
        self.current_angle %= 360
        return self.current_angle

    #measure motor temperature
    def readTemperature(self):
        #TODO: Add filter?
        meas_temp = self.bus.read_byte_data(self.address, self.TEMPERATURE_L_ADDRESS) #request and read temperature
        if meas_temp < 100: #why? do "false readings" show up as high numbers?
            self.temperature = meas_temp
        return self.temperature

    #adds hysteresis to the overheating - should only continue after having cooled down considerably
    def isOverheated(self):
        if self.temperature <= self.RESTART_TEMP:
            self.overheated=False
        elif self.temperature >= self.MAX_TEMP:
            self.overheated=True
        return self.overheated


    #check whether leg has finished its movement
    def isDone(self):
        return self.relaxed or (not self.forced and not self.enabled) or (abs_angle_difference(self.current_angle,self.target_angle)<=self.DELTA_ANGLE)
        #if the leg is relaxed, it has not target so it is always in place
        #if the leg is disabled, neglect it, unless force was specified
        #else, check whether the angle is close to the target angle

    #check if leg is stuck by looking at the current and expected position and timing
    def isStuck(self,time):

        
        
        #method 1: check if the leg hasn't arrived in time
        if time-self.LEG_STUCK_DELAY>self.delta_time*self.LEG_STUCK_FACTOR: #leg is busy for a long time (obsolete, just for extra safety)

            if DEBUG:
                print("Leg %d"%self.leg_num)
                print("Too much time passed:",time)
                print(self.log)
            
            return True

        #method 2: check if the leg is on the right track
        if self.direction=="f":
            abs_progress=(self.current_angle-self.prev_angle)%360
        else:
            abs_progress=(self.prev_angle-self.current_angle)%360

        self.progress+=angle_difference(abs_progress,self.progress) #set progress to the nearest value of abs_progress to avoid overshoot/undershoot giving weird angles


        if DEBUG:
            self.log.append(dict(time=time,progress=self.progress,dt=self.delta_angle,da=self.delta_angle,angle=self.current_angle,prev=self.prev_angle,next=self.target_angle,bound=((time-self.LEG_STUCK_DELAY)*self.delta_angle)/(self.delta_time*self.LEG_STUCK_FACTOR)))


        #if progress < intended progress
        #progress < time*speed
        #progress < time*(da/dt)
        #progress*dt < (time-30)*da
        #progress/da < time/dt -> bad
        #speedf * progress/da < (time-offset)/dt
        #speedf * progress * dt < (time-offset) * da
        #if progress<time/self.delta_time*self.delta_angle: #leg hasn't progressed as much as it should have
        if self.progress*self.delta_time*self.LEG_STUCK_FACTOR < (time-self.LEG_STUCK_DELAY)*(self.delta_angle): #0 angle difference means delta_time must be 0 as well, and it won't fail
            if DEBUG:
                print("Leg %d"%self.leg_num)
                print("Leg got stuck: lagging behind too much")
                print(self.log)
            return True
        return False
        
        # stuck when either: position<<expected position or time>>max time


    #in disabled state, the leg won't move unless specifying force
    def enable(self):
        self.enabled=True
    def disable(self):
        self.enabled=False

    #relax - turn off motor completely
    def relax(self):
        self.sendCommand(0,0,10) #illegal direction results in leg relaxation
        self.relaxed=True

    #send commands to the leg driver
    def sendCommand(self, position, direction, deltaTime): #write data to motor driver
        #set self.target_angle
        position = (position+self.DELTA_SIDE)%360 #correction for right legs

        position = position / 3

        self.bus.write_byte_data(self.address, self.DIRECTION_ADDRESS, int(direction)) #2=FD, 3=BD (motors know their direction?!)
        self.bus.write_byte_data(self.address, self.POSITION_ADDRESS, int(position)) #number between 0-119
        self.bus.write_byte_data(self.address, self.TIME_ADDRESS, int(deltaTime)) # measure for the time the movement should take. 50/s?

    #for sending more complex commands (with named positions, speeds, etc)
    def smartCommand(self,position,direction,time=None,speed=None,force=False):
        #only run disabled motor when forced
        if not(force or self.enabled):
            return #disabled leg is neglected without force
        
        #position
        if position==LEG_POS_UP:
            pos=self.LIEDOWN_ANGLE
        elif position==LEG_POS_DOWN:
            pos=self.STANDUP_ANGLE
        elif position==LEG_POS_LIFTOFF:
            pos=self.LIFTOFF_ANGLE
        elif position==LEG_POS_TOUCHDOWN:
            pos=self.TOUCHDOWN_ANGLE
        elif position==LEG_POS_CURRENT:
            pos=self.current_position #will this work???
        else:
            pos=position

        pos=pos//3 * 3#ensure there are no weird situations due to the position not being an exact position

        #direction
        if direction==LEG_DIR_FORWARDS:
            dir="f"
        elif direction==LEG_DIR_BACKWARDS:
            dir="b"
        elif direction==LEG_DIR_CW:
            dir={"left":"b","right":"f"}[self.legSide]
        elif direction==LEG_DIR_CCW:
            dir={"left":"f","right":"b"}[self.legSide]
        elif direction==LEG_DIR_CLOSEST or direction==LEG_DIR_SAFE:
            if angle_between(pos,self.current_angle,self.current_angle+180):
                dir="f"
            else:
                dir="b"
        elif s["direction"]==LEG_DIR_SAFE and dir=="b":#if the leg moves backwards in some region [A,B], turn forwards instead to prevent high torque
            if angle_between(pos,self.SAFE_ANGLE_A,self.SAFE_ANGLE_B) or angle_between(self.current_angle,self.SAFE_ANGLE_A,self.SAFE_ANGLE_B) or\
               angle_between(self.SAFE_ANGLE_A,pos,pos+(self.current_angle-pos)%360): #between pos and current angle, making sure current_angle>pos
                dir="f"

        #time/speed
        if dir=="f":
            delta_angle=(pos-self.current_angle)%360
        else:
            delta_angle=(self.current_angle-pos)%360
        
        if time!=None:
            delta_time=time
        else:
            if speed==None: speed=LEG_SPEED_NORMAL

            if speed==LEG_SPEED_SLOW:
                delta_time=delta_angle/self.SPEED_SLOW
            elif speed==LEG_SPEED_FAST:
                delta_time=delta_angle/self.SPEED_FAST
            else:# speed=="normal":
                delta_time=delta_angle/self.SPEED_NORMAL


        #make sure time is a proper time (speed is within bounds)
        time_min=delta_angle/self.SPEED_MAX
        time_max=delta_angle/self.SPEED_MIN
        if DEBUG:   print(f"leg:{self.leg_num}\tDA:{delta_angle}\tDT:{delta_time}\tDTN:{time_min}\tDTX:{time_max}")
        
        if delta_time>time_max or delta_time<time_min:
            self.master.returnf(self.master._warning("Improper leg time for leg %d corrected to fit angle difference"%self.leg_num))#print("Improper timing - corrected")

        delta_time=int(min(time_max,max(time_min,delta_time)))
        #time -3???? this was in the old code but I don't know why
        

        #send commands
        dir2={"f":2,"b":3}[dir]


        self.sendCommand(pos,dir2,delta_time)

        #store command data for checking for stuck legs etc.
        self.direction=dir
        self.prev_angle=self.current_angle
        self.progress=0
        self.delta_time=delta_time
        self.delta_angle=delta_angle
        self.target_angle=pos
        self.forced=force

        #moving so not relaxed (anymore)
        self.relaxed=False

        #for debugging when leg got stuck
        if DEBUG:
            self.log=[]







        

