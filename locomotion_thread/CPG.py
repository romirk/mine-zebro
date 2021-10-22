# Central Pattern Generator
import numpy as np
import time


# get named values instead of strings
from locomotion_constants import *


DEBUG = 0

class CPG:
    def __init__(self, legs):
        self.legs = legs
        self.step_number=0

        self.leg_groups=[(1,4,5),(2,3,6)]


    #generate motor instructions from higher level steps such as "left" and "forwards"
    def create_step(self,direction):
        if DEBUG:
            print("cpg: step_number = " + str(self.step_number))
            
        groupA,groupB=self.leg_groups[self.step_number%2],self.leg_groups[(self.step_number+1)%2] #switch groups every step
        
        self.step_number+=1

        #speed="normal"


        if direction==STEP_FORWARDS:
            if DEBUG:
                print("cpg: straight ahead")
            return [dict(motors=groupA,position="touchdown",direction="forwards",speed="fast"),\
                dict(motors=groupB,position="liftoff",direction="forwards",speed="normal")]

        elif direction==STEP_BACKWARDS:
            #groupA,groupB=groupB,groupA #reverse groups so that the robot can just walk backwards without having to reset the legs
            if DEBUG:
                print("cpg: straight backwards")
            return [dict(motors=groupA,position="touchdown",direction="backwards",speed="normal"),\
                dict(motors=groupB,position="liftoff",direction="backwards",speed="fast")]

        elif direction==STEP_LEFT:
            # turn left fully
            if DEBUG:
                print("cpg: direction is left")
            return [dict(motors=[leg for leg in groupA if self.legs[leg-1].legSide=="left"],position="liftoff",direction="backwards",speed="fast"),\
                dict(motors=[leg for leg in groupA if self.legs[leg-1].legSide=="right"],position="touchdown",direction="forwards",speed="fast"),\
                dict(motors=[leg for leg in groupB if self.legs[leg-1].legSide=="left"],position="touchdown",direction="backwards",speed="normal"),\
                dict(motors=[leg for leg in groupB if self.legs[leg-1].legSide=="right"],position="liftoff",direction="forwards",speed="normal")]  
                

        elif direction==STEP_RIGHT:
            #groupA,groupB=groupB,groupA #reverse groups so that the robot can just turn
            if DEBUG:
                print("cpg: direction is right")
            # turn right fully
            return [dict(motors=[leg for leg in groupA if self.legs[leg-1].legSide=="right"],position="liftoff",direction="backwards",speed="fast"),\
                dict(motors=[leg for leg in groupA if self.legs[leg-1].legSide=="left"],position="touchdown",direction="forwards",speed="fast"),\
                dict(motors=[leg for leg in groupB if self.legs[leg-1].legSide=="right"],position="touchdown",direction="backwards",speed="normal"),\
                dict(motors=[leg for leg in groupB if self.legs[leg-1].legSide=="left"],position="liftoff",direction="forwards",speed="normal")]  

        elif direction == STEP_DOWN:
            if DEBUG:
                print("cpg: lying down")
            return [dict(motors=[1,2,3,4,5,6],position="up")]

        elif direction == STEP_UP:
            if DEBUG:
                print("cpg: standing up")
            return [dict(motors=[1,2,3,4,5,6],position="down",direction="safe")]
            
        elif direction == STEP_SIT:
            if DEBUG:
                print("cpg: sitting")
            return [dict(motors=[3,4,5,6],position="up"),dict(motors=[1,2],position="down")]
            
        elif direction == STEP_BOW:
            if DEBUG:
                print("cpg: bowing")
            return [dict(motors=[1,2,3,4],position="up"),dict(motors=[5,6],position="down")]
        elif direction == STEP_RELAX:
            if DEBUG:
                print("cpg:relax")
            return [dict(motors=[1,2,3,4,5,6],relax=True)]
            
