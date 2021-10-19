from math import floor
from time import sleep


def angle_between(x,a,b): #assert a<=b
    while x>b:  x-=360 #ensure x is minimal
    while x<a:  x+=360 #ensure a<=a
    return x<=b #test if a<x<b

def abs_angle_difference(a,b):
    return abs((b-a+180)%360-180) #convert difference to [-180,180] interval

class ZebroLeg:
    def __init__(self, leg_num, bus, master):
        self.leg_num = leg_num+1
        self.address = self._address()
        self.bus=bus
        self.master=master

        #addresses
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

        self.SAFE_ANGLE_A=200
        self.SAFE_ANGLE_B=300

        #speeds (degrees/50Hz tick)
        self.SPEED_MAX=7.2#round in 1sec
        self.SPEED_MIN=2#fully round in 3.6s
        self.SPEED_FAST=7
        self.SPEED_NORMAL=5
        self.SPEED_SLOW=3#some arbitrary value?



        #correction angles
        self.DELTA_ANGLE = 5 #leeway
        self.DELTA_RIGHT = 5 #correction for right leg

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

        #leg stuck detection
        self.prev_angle=self.current_angle
        self.delta_time=1
        self.direction="f"

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




    def sendEvent(self, deltaTime, type):  # type 0: liftoff, 1 = step; forwards stepping?
        if type == 0:
            position = self.TOUCHDOWN_ANGLE
        else:
            position = self.LIFTOFF_ANGLE
        position += self.DELTA_SIDE  #right leg position correction?
        deltaTime = floor(deltaTime / self.TIME_DIVISOR) - 3 #what does -3 do?????
        self.sendCommand(2, position, deltaTime)
        self.target_angle = position



    def readAngle(self): #read leg position
        self.current_angle = self.bus.read_byte_data(self.address, self.LEG_POSITION_ADDRESS) * 3 #request angle and convert to degrees

        self.current_angle-=self.DELTA_SIDE
        self.current_angle %= 360
        return self.current_angle

    def readTemperature(self): #measure motor temperature
        #TODO: Add filter?
        meas_temp = self.bus.read_byte_data(self.address, self.TEMPERATURE_L_ADDRESS) #request and read temperature
        if meas_temp < 100: #why? do "false readings" show up as high numbers?
            self.temperature = meas_temp
        return self.temperature


    
    def isOverheated(self):
        if self.temperature <= self.RESTART_TEMP:
            self.overheated=False
        elif self.temperature >= self.MAX_TEMP:
            self.overheated=True
        return self.overheated


    def isDone(self): #need a fix for forces commands!
        return self.relaxed or (not self.forced and not self.enabled) or (abs_angle_difference(self.current_angle,self.target_angle)<=self.DELTA_ANGLE)
        #if the leg is relaxed, it has not target so it is in place
        #if the leg is disabled, neglect it, unless force was specified
        #else, check whether the angle is close to the target angle

    def isStuck(self,time):
        if time-30>self.delta_time*1.5: #leg is busy for a long time (obsolete, just for extra safety)
            return True

        if self.direction=="f":
            progress=(self.current_angle-self.prev_angle)%360
        else:
            progress=(self.prev_angle-self.current_angle)%360


        #if progress < intended progress
        #progress < time*speed
        #progress < time*(da/dt)
        #progress*dt < (time-30)*da
        #if progress<time/self.delta_time*self.delta_angle*1.5: #leg hasn't progressed as much as it should have
        if progress*self.delta_time*1.5 < (time-30)*(self.delta_angle+1) #+1 to fix 0 angle difference
            return True
        return False
        
        # stuck when either: position<<expected position or time is too large


    def enable(self):
        self.enabled=True
    def disable(self):
        self.enabled=False


    def relax(self):
        self.sendCommand(0,0,10) #illegal direction results in leg relaxation
        self.relaxed=True

    def sendCommand(self, position, direction, deltaTime): #write data to motor driver
        #set self.target_angle
        position = (position+self.DELTA_SIDE)%360 #correction for right legs

        position = position / 3

        self.bus.write_byte_data(self.address, self.DIRECTION_ADDRESS, int(direction)) #2=FD, 3=BD (motors know their direction?!)
        self.bus.write_byte_data(self.address, self.POSITION_ADDRESS, int(position)) #number between 0-119
        self.bus.write_byte_data(self.address, self.TIME_ADDRESS, int(deltaTime)) # measure for the time the movement should take. 50/s?


    def smartCommand(self,position,direction,time=None,speed=None,force=False):
        #only run disabled motor when forced
        if not(force or self.enabled):
            return
        
        #position
        if position=="up":
            pos=self.LIEDOWN_ANGLE
        elif position=="down":
            pos=self.STANDUP_ANGLE
        elif position=="liftoff":
            pos=self.LIFTOFF_ANGLE
        elif position=="touchdown":
            pos=self.TOUCHDOWN_ANGLE
        elif position=="current":
            pos=self.current_position #will this work???
        else:
            pos=position

        #direction
        if direction=="forwards":
            dir="f"
        elif direction=="backwards":
            dir="b"
        elif direction=="cw":
            dir={"left":"b","right":"f"}[self.legSide]
        elif direction=="ccw":
            dir={"left":"f","right":"b"}[self.legSide]
        elif direction=="closest" or direction=="safe":
            if angle_between(pos,self.current_angle,self.current_angle+180):
                dir="f"
            else:
                dir="b"
        elif s["direction"]=="safe" and dir=="b":#if the leg moves backwards in some region [A,B], turn forwards instead to prevent high torque
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
            if speed==None: speed="normal"

            if speed=="slow":
                delta_time=delta_angle/self.SPEED_SLOW
            elif speed=="fast":
                delta_time=delta_angle/self.SPEED_FAST
            else:# speed=="normal":
                delta_time=delta_angle/self.SPEED_NORMAL


        #make sure time is a proper time (speed is within bounds)
        time_min=delta_angle/self.SPEED_MAX
        time_max=delta_angle/self.SPEED_MIN
        print(f"leg:{self.leg_num}\tDA:{delta_angle}\tDT:{delta_time}\tDTN:{time_min}\tDTX:{time_max}")
        
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
        self.delta_time=delta_time
        self.delta_angle=delta_angle
        self.target_angle=pos
        self.forced=force

        #moving so not relaxed (anymore)
        self.relaxed=False







        

