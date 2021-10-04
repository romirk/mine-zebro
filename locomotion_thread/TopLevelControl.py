# Top level controller of the locomotion
# The locomotion is a rewritten version of the one written by Laurens Kinkelaar
# More information about that version is in his thesis
# More information about this version is in the readme

# Author: Frank van Veelen
# Date: 04/02/19
from ZebroLeg import ZebroLeg
from smbus2 import SMBus
import time
from multiprocessing.connection import Listener
import CPG

MAX_TEMPERATURE = 45
START_TEMP = 35
NUMBER_OF_LEGS = 6
DEBUG = 0

LegArray = []
bus = SMBus(1)

# blocking read, waits for other end of socket to connect
# (could come from the ZebroPiController2.py file)
address = ('localhost', 6000)
listener = Listener(address, authkey=b'zebro')
conn = listener.accept()
print("Connection accepted from: ", listener.last_accepted)

def coolDown(cooldown_time):
    for leg in LegArray:
        leg.lieDown(cooldown_time, bus)
    time.sleep(30)
    return 0

# creating leg objects
for i in range(0, NUMBER_OF_LEGS):
    LegArray.append(ZebroLeg(i, bus))  # creating leg array

for leg in LegArray:
    leg.standUp(bus)

time.sleep(1.1)  # must be larger than 1, as each leg gets a a 1 sec hardcoded time in standUp function

# speed:
speed = 0 # number between 0 and 5
direction = 0 # number between 0 and 9
old_speed = speed
old_direction = direction

CPG = CPG.CPG(NUMBER_OF_LEGS, 2, 0.5, 0.1, 0.05, LegArray, bus, speed, direction)

def readState():
    global speed, direction, old_speed, old_direction
    old_speed = speed
    old_direction = direction
    [speed, direction] = conn.recv()
    if (DEBUG): print("TLC-L new speed, direction is:\t" + str([speed, direction]))

def leg_is_stuck(time_out_counter):
    if (time_out_counter > 10):
        return True
    else:
        return False


step_number = 0

if(DEBUG): print("TLC-L In loop now")

while True:

    # TEMPERATURE CHECK
    if(step_number % 10 == 0):
        max_temp = 0
        for i in LegArray:
            temp = i.measure_temperature(bus)
            if temp > max_temp:
                max_temp = temp
        if max_temp > MAX_TEMPERATURE:
            if(DEBUG): print("TLC-L Maximum Motor temperature reached, sleeping for 60 seconds, temperature was; " + str(max_temp))
            while max_temp > START_TEMP:
                coolDown(60)
                for i in LegArray:
                    temp = i.measure_temperature(bus)
                    if temp > max_temp:
                        max_temp = temp

    CPG.send_step(step_number)

    # Wait for all legs to reach their desired angle
    legs_done = 0

    # array with six values that count the number of timeouts
    # that a leg needs to get to a certain position
    # if that exceeds the limits, we assume a leg to be
    # stuck and we continue
    time_out_counter = [0] * NUMBER_OF_LEGS
    stuck_leg = False

    time.sleep(0.6) #for if steps are send too fast
    # TODO make sure this cant be called before step is being started as a step will be skipped
    while(not legs_done and not stuck_leg):
        for leg in LegArray:
            leg.readLegAngle(bus) #update leg angle known by the pi
            if DEBUG:
                print("TLC-L leg " + str(leg.leg_num) +" angle is: " + str(leg.legAngle))
                print("TLC-L leg " + str(leg.leg_num) +" des angle is: " + str(leg.desAngle))
                print("TLC-L leg " + str(leg.leg_num) +" angle diff is: " + str(abs(leg.legAngle - leg.desAngle)))
            if abs(leg.legAngle - leg.desAngle) < 55:
                if DEBUG:
                    print("TLC-L leg " + str(leg.leg_num) +" in position")
                legs_done = 1
            else:
                time_out_counter[leg.leg_num-1] += 1;
                if DEBUG:
                    print("TLC-L legs not done yet")
                    print("TLC-L LegAngle "+ str(leg.leg_num) +": " + str(leg.legAngle) + ", Desired angle: " + str(leg.desAngle))
                time.sleep(0.1)
                if (leg_is_stuck(time_out_counter[leg.leg_num - 1])):
                    stuck_leg = True
                    if DEBUG: print("********TLC-L: leg " + str(leg.leg_num) + "is stuck********")
                    continue
                break

    if DEBUG:
        print("TLC-L step completed")
    step_number += 1
    conn.send("done")

    readState()

    if DEBUG:
        print("TLC-L CPGSpeed is now:" + str(CPG.speed))
    if old_speed != speed or old_direction != direction:  # change in walkstyle > change in gait
        if DEBUG:
            print("TLC-L Changing walkstyle")
            print("TLC-L Speed = " + str(speed) + ", Direction = " + str(direction))
        time.sleep(1)  # wait for last step to complete
        for Leg in LegArray:
            if DEBUG: print("------------------TLC-L to stand up position--------------")
            Leg.standUp(bus)  # No dynamic gait switching, reliability
        time.sleep(1)  # wait for stand-up to complete
        CPG.updateParameters(speed, direction)
        if DEBUG:
            print("CPGSpeed is now:" + str(CPG.speed))


