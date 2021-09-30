#!/usr/bin/env python3
import serial
import time
import sys
import math
import random
from multiprocessing.connection import Client

SOCKET_ON = 0
DEBUG = 1

# DOES NOT WORK WITH PYTHON 2. RUN AS "./py.py <file>"

#define ZEBROBUS_OBS_MASTER_READ 			0xF0
#define ZEBROBUS_OBS_MASTER_WRITE 			0x0F
#define VREGS_OBS_INFRAREDRAW_L 	0x50
#define VREGS_OBS_INFRAREDRAW_H 	0x51
#define VREGS_OBS_DISTANCERAW0		0x52
#define VREGS_OBS_DISTANCERAW1		0x53
zoneWallConsider = 85.0
zoneWallMinimum = 45.0
if SOCKET_ON:
    address= ('localhost', 6000)
    conn = Client(address, authkey=b'zebro')

def zebroMapping(zebroSpeed, zebroRotation):
    # zebroRotation mapping to {-1, 1} to comply with interface
    zebroRotation = math.sin(zebroRotation)
    # Minimum turning value for physical reasons
    if (abs(zebroRotation) < 0.3) and (zebroRotation != 0.0):
        zebroRotation = (zebroRotation/abs(zebroRotation)) * 0.3
    zebroRotation = round((zebroRotation*4.0)+5.0)
    zebroSpeed = round(zebroSpeed*5.0)
    return zebroSpeed, zebroRotation

def zebroReverseMapping(speed, rotation):
    zebroRotation = (rotation - 5) / 4.0
    zebroSpeed = speed/5.0
    return zebroSpeed, zebroRotation

def get_array():
    register = 0x30
    length = 11
    data_arr = [0xF0, register, length]
    ser.write(bytearray(data_arr));
    data = ser.read(length)
    return([int(n.encode("hex"), 16) for n in data])


def write_to_file(speed, angle):
    #with open("WalkStyle.txt", 'w') as f:
    #    f.write(str(int(speed)) + " " + str(int(angle)))
    if SOCKET_ON:
        conn.send([int(speed), int(angle)])
    else:
        print("ZPC2: write to file speed angle: " + str(speed) + " " + str(angle))

class Vector:
	def __init__(self, x, y):
		self.x = x
		self.y = y
	def add(self, v):
		self.x += v.x
		self.y += v.y

class WallData:
    WallSenseAngle = math.radians(15.0)
    Angle = []
    for i in range(11):
        Angle.append((i - 5.0) * WallSenseAngle) #mapping sensors to angles, 0 to 11 to -75 to 75 degrees

    def __init__(self, arr):
        self.Distance = []
        for i in arr:
            self.Distance.append(i)

def AvoidWalls(wallData): #preferable, werkt vrij goed met DeciZebro met 2 ogen
        zebroRotation = 0.0
        zebroSpeed = 1.0
        for i in range(len(wallData.Angle)):
            if(wallData.Distance[i] < zoneWallMinimum):

                if(abs(zebroRotation) < abs(wallData.Angle[i])):
                    zebroRotation = wallData.Angle[i]

                zebroSpeed = min(zebroSpeed, (1 - math.cos(wallData.Angle[i])))

            elif(wallData.Distance[i] < zoneWallConsider):

                ratio = (1-(wallData.Distance[i] - zoneWallMinimum)/(zoneWallConsider-zoneWallMinimum)) #maps distance (45->110) to (1->0)

                if(abs(zebroRotation) < abs(wallData.Angle[i] * ratio)):

                    zebroRotation = wallData.Angle[i] * ratio

                zebroSpeed = min(zebroSpeed, math.cos(wallData.Angle[i]) * ratio)

        return zebroMapping(zebroSpeed, zebroRotation)


def UseTwoEyes(wallData, previous_rotation):
    _, previousZebroRotation = zebroReverseMapping(0, previous_rotation)

    zebroRotation = 0
    zebroSpeed = 0

    wds = (wallData.Distance[0], wallData.Distance[-1])

    mindist = min(wds[0], wds[1])
    zebroSpeed = min(mindist/50.0, 1.0)

    # if everything is too small keep rotating in the way we were. If rotation
    # is zero, choose a direction
    if wds[0] < zoneWallMinimum and wds[1] < zoneWallMinimum and previousZebroRotation < 0.1:
        zebroRotation = random.choice([-1.0, 1.0])
        zebroSpeed = 0

    elif wds[0] < zoneWallMinimum and wds[1] < zoneWallMinimum:
        if previousZebroRotation < 0:
            zebroRotation = -1.0
        else:
            zebroRotation = 1.0
        zebroSpeed = 0

    # no space left -> go right
    elif wds[0] < zoneWallMinimum:
        zebroRotation = 1.0
        zebroSpeed = 0

    # no space right -> go left
    elif wds[1] < zoneWallMinimum:
        zebroRotation = -1.0
        zebroSpeed = 0

    # Here nothing is below minimum, so check the tightest corner we would need
    # to make otherwise
    else:
        zebroRotationRight = 1 - min(1.0, wds[0]/zoneWallConsider)
        zebroRotationLeft = 1 - min(1.0, wds[1]/zoneWallConsider)

        if (zebroRotationLeft < zebroRotationRight):
            zebroRotation = -zebroRotationLeft
        else:
            zebroRotation = zebroRotationRight

    return zebroMapping(zebroSpeed, zebroRotation)

def LargestConeWallAvoidance(wallData): #werkt niet voor nu, eventueel met meer sensoren
    coneExtend = 1
    scores = [0]*11

    for i in range(len(wallData.Distance)):
        for j in range(i-coneExtend, i+coneExtend+1):
            if j>=0 and j < 11:
                scores[i] += wallData.Distance[j]
            else:
                scores[i] += wallData.Distance[i]

    checkOrder = (5,4,6,3,7,2,8,1,9,0,10)
    foundCone = False
    for i in checkOrder:
        if scores[i]>zoneWallConsider*4.0:
            zebroRotation = wallData.Angle[i]
            foundCone = True
            break
    if not foundCone:
        zebroRotation = wallData.Angle[0] #IF no good cone just go left

    if foundCone:
        # can have speed > 0
        minFrontDist = min(wallData.Distance[3:8])
        if minFrontDist < 80:
            zebroSpeed = minFrontDist/80.0
        else:
            zebroSpeed = 1
    else:
        zebroSpeed = 0


    return zebroMapping(zebroSpeed, zebroRotation)

if __name__ == '__main__':
    #if len(sys.argv) != 2:
    #    print("expected serial port as argument")
    #    exit(1);

    arg = "/dev/serial0"
    ser = serial.Serial(arg , 38400, timeout=1)

    time.sleep(2)

    speed = 0
    angle = 5

    ser.write(bytearray([0xFF]));
    while(True):
        arr = get_array()
        print(arr)

    # ser.write(bytearray([0xFF]));
    while True:
        arr = get_array()
        arr = list(reversed(arr))
        print(arr)
        wallData = WallData(arr)
        speed, angle = AvoidWalls(wallData)
        #speed, angle = LargestConeWallAvoidance(wallData)
        #speed, angle = UseTwoEyes(wallData, angle)
        # write_to_file(speed, angle)
        if(DEBUG): print("ZPC2: speed, angle is" + str(speed) + " " + str(angle) )
        #time.sleep(2)

