from math import floor
from time import sleep


def angle_between(x,a,b): #assert a<=b
    while x>b:  x-=360 #ensure x is minimal
    while x<a:  x+=360 #ensure a<=a
    return x<=b #test if a<x<b

def abs_angle_difference(a,b):
    return abs((b-a+180)%360-180) #convert difference to [-180,180] interval

class ZebroLeg:
    def __init__(self, leg_num, bus):
        self.leg_num = leg_num+1
        self.address = self.address() #ugly code
        self.TEMPERATURE_L_ADDRESS = 0x41
        # self.TEMPERATURE_H_ADDRESS = 0x42
        self.LEG_POSITION_ADDRESS = 0x40
        self.DIRECTION_ADDRESS = 0x20
        self.POSITION_ADDRESS = 0x21
        self.TIME_ADDRESS = 0x22
        self.legAngle = 0
        self.onGround = True #unused?
        self.angleCorrect = True #unused?
        self.legDelayed = False #unused?
        self.delayTime = 0 #unused?
        self.startDelay = 0 #unused?
        self.sendAngle = 0 #unused? (desAngle?)
        self.LIEDOWN_ANGLE = 330
        self.STANDUP_ANGLE = 150
        self.TOUCHDOWN_ANGLE = 125
        self.LIFTOFF_ANGLE = 160
        self.deltaAngle = 5
        self.deltaRight = 5
        self.TIME_DIVISOR = 0.02
        self.legCheck = True
        self.desAngle = self.readLegAngle(bus)

        if self.leg_num % 2 == 0:
            self.legSide = "right"
        else:
            self.legSide = "left"

    def address(self):
        leg_address = {
            1: 0x48,
            2: 0x58,
            3: 0x68,
            4: 0x78,
            5: 0x28,
            6: 0x38
        }[self.leg_num]
        return leg_address

    def sendEvent(self, deltaTime, type, bus):  # type 0: liftoff, 1 = step; forwards stepping?
        if type == 0:
            position = self.TOUCHDOWN_ANGLE
        else:
            position = self.LIFTOFF_ANGLE
        if self.leg_num % 2 == 0:
            position += self.deltaRight  #right leg position correction?
        deltaTime = floor(deltaTime / self.TIME_DIVISOR) - 3 #what does deltaTime do?????
        self.sendCommand(2, position, deltaTime, bus)
        self.desAngle = position

    def sendEventBack(self, deltaTime, type, bus):  # type 0: liftoff, 1 = step; backwards stepping?
        if type == 0:
            position = self.TOUCHDOWN_ANGLE
        else:
            position = self.LIFTOFF_ANGLE
        if self.leg_num % 2 == 0:
            position = position + self.deltaRight
        deltaTime = floor(deltaTime / self.TIME_DIVISOR) - 3
        self.sendCommand(3, position, deltaTime, bus)
        self.desAngle = position

    def readLegAngle(self, bus): #read leg position
        self.legAngle = bus.read_byte_data(self.address, self.LEG_POSITION_ADDRESS) * 3 #request angle and convert to degrees
        #self.onGround = ((self.legAngle < (self.LIFTOFF_ANGLE + self.deltaAngle)) and (self.legAngle > (self.TOUCHDOWN_ANGLE - self.deltaAngle)))
        self.onGround = (abs_angle_difference(self.legAngle,self.LIFTOFF_ANGLE)<self.deltaAngle) #unused?
        return self.legAngle

    def measure_temperature(self, bus): #measure motor temperature (why is this not camelCase?)
        #TODO: Add filter?
        temp = 25
        meas_temp = bus.read_byte_data(self.address, self.TEMPERATURE_L_ADDRESS) #request and read temperature
        if meas_temp < 100: #why? do "false readings" show up as high numbers?
            temp = meas_temp
        return temp

    def lieDown(self, bus): #move leg up - should be changed to prefer moving backwards!
        self.readLegAngle(bus)
        if self.legAngle < self.LIEDOWN_ANGLE:
            self.sendCommand(3, self.LIEDOWN_ANGLE, 1, bus)
            self.desAngle = self.LIEDOWN_ANGLE
        else:
            self.sendCommand(2, self.LIEDOWN_ANGLE, 1, bus)
            self.desAngle = self.LIEDOWN_ANGLE

    def standUp(self, bus): #move leg down - should be changed to prefer moving forwards!
        self.readLegAngle(bus)
        if self.legAngle > self.STANDUP_ANGLE + self.deltaAngle:
            self.sendCommand(3, self.STANDUP_ANGLE, 1, bus)
            self.desAngle = self.STANDUP_ANGLE
        elif self.legAngle < self.STANDUP_ANGLE - self.deltaAngle:
            self.sendCommand(2, self.STANDUP_ANGLE, 1, bus)
            self.desAngle = self.STANDUP_ANGLE


    def sendCommand(self, direction, position, deltaTime, bus): #write data to motor driver
        position %= 360

        position = position / 3

        bus.write_byte_data(self.address, self.DIRECTION_ADDRESS, int(floor(direction))) #either 2 or 3...? does the leg know it's side?
        bus.write_byte_data(self.address, self.POSITION_ADDRESS, int(floor(position))) #number between 0-120? (I think the disks have 30 holes)
        bus.write_byte_data(self.address, self.TIME_ADDRESS, int(floor(deltaTime))) #???

    #unused?
    def sendPosition(self, deltaTime, position, bus):
        self.readLegAngle(bus)
        if self.leg_num % 2 == 0:
            position += self.deltaRight
        deltaTime = floor(deltaTime / self.TIME_DIVISOR) - 3
        self.sendCommand(2, position, deltaTime, bus)
        self.desAngle = position

    #unused?
    def sendPositionBack(self, deltaTime, position, bus):
        if position > (self.legAngle + self.deltaAngle) or position < (self.legAngle - self.deltaAngle):
            if self.leg_num % 2 == 0:
                position += self.deltaRight
            deltaTime = floor(deltaTime / self.TIME_DIVISOR) - 3
            self.sendCommand(3, position, deltaTime, bus)
            self.desAngle = position
    #unused?
    def checkDelay(self,Time ,eventList, bus):  # Checks for delays in this leg
        #if self.legAngle > (self.desAngle - self.deltaAngle) and self.legAngle < (self.deltaAngle + self.desAngle):
        if abs_angle_difference(self.legAngle,self.desAngle)<self.deltaAngle:
            self.delayTime = 0
            self.startDelay = 0
        else:
            if self.startDelay == 0:
                self.startDelay = eventList[self.leg_num - 1][0]
            self.delayTime = Time - self.startDelay
