# Central Pattern Generator
import numpy as np
import time

DEBUG = 0

class CPG:
    def __init__(self, NoL, NLG, tf, tg, td, legArray, bus, speed, direction):
        self.NumLegGroups = NLG
        self.legArray = legArray
        self.NoL = NoL
        self.tf = tf
        self.tg = tg
        self.td = td
        self.bus = bus
        self.speed = speed
        self.direction = direction

        if self.NumLegGroups == 1:
            self.gaitOrder = self.Hopping()
        elif self.NumLegGroups == 2:
            self.gaitOrder = self.Tripod()  # most reliable, only one implemented for now.
        elif self.NumLegGroups == 3:
            self.gaitOrder = self.Quadrapod()
        elif self.NumLegGroups == 4:
            self.gaitOrder = self.ZebroGallop()
        elif self.NumLegGroups == 6:
            self.gaitOrder = self.Pentapod()
        else:
            print("invalid number of leg groups")

    def updateParameters(self, speed, direction):
        self.speed = speed
        self.direction = direction

    def send_step(self, step_number):  # TRIPOD ONLY
        # TODO: Fix for other leg groups
        if DEBUG:
            print("cpg: step_number = " + str(step_number))
            print("cpg: speed = " + str(self.speed) + " direction = " + str(self.direction))

        if self.speed == 5 and self.direction == 5:
            if DEBUG:
                print("cpg: straight ahead")
            if step_number % self.NumLegGroups == 0:
                for i in self.gaitOrder[0]:
                    self.legArray[i - 1].sendEvent(self.tf, 0, self.bus)
                for i in self.gaitOrder[1]:
                    self.legArray[i - 1].sendEvent(self.tg, 1, self.bus)
            else:
                for i in self.gaitOrder[0]:
                    self.legArray[i - 1].sendEvent(self.tg, 1, self.bus)
                for i in self.gaitOrder[1]:
                    self.legArray[i - 1].sendEvent(self.tf, 0, self.bus)

        elif self.speed == 0 and self.direction == 1:
            # turn left fully
            if DEBUG:
                print("cpg: direction is left")
            if step_number % self.NumLegGroups == 0:
                for i in self.gaitOrder[0]:
                    if self.legArray[i - 1].legSide == "right":
                        self.legArray[i - 1].sendEvent(self.tg, 0, self.bus)
                    else:
                        self.legArray[i - 1].sendEventBack(self.tf, 1, self.bus)
                for i in self.gaitOrder[1]:
                    if self.legArray[i - 1].legSide == "right":
                        self.legArray[i - 1].sendEvent(self.tf, 1, self.bus)
                    else:
                        self.legArray[i - 1].sendEventBack(self.tg, 0, self.bus)
            elif step_number % self.NumLegGroups == 1:
                for i in self.gaitOrder[0]:
                    if self.legArray[i - 1].legSide == "right":
                        self.legArray[i - 1].sendEvent(self.tf, 1, self.bus)
                    else:
                        self.legArray[i - 1].sendEventBack(self.tg, 0, self.bus)
                for i in self.gaitOrder[1]:
                    if self.legArray[i - 1].legSide == "right":
                        self.legArray[i - 1].sendEvent(self.tg, 0, self.bus)
                    else:
                        self.legArray[i - 1].sendEventBack(self.tf, 1, self.bus)

        elif self.speed == 0 and self.direction == 9:
            if DEBUG:
                print("cpg: direction is right")
            # turn right fully
            if step_number % self.NumLegGroups == 0:
                for i in self.gaitOrder[1]:
                    if self.legArray[i - 1].legSide == "left":
                        self.legArray[i - 1].sendEvent(self.tg, 0, self.bus)
                    else:
                        self.legArray[i - 1].sendEventBack(self.tf, 1, self.bus)
                for i in self.gaitOrder[0]:
                    if self.legArray[i - 1].legSide == "left":
                        self.legArray[i - 1].sendEvent(self.tf, 1, self.bus)
                    else:
                        self.legArray[i - 1].sendEventBack(self.tg, 0, self.bus)
            elif step_number % self.NumLegGroups == 1:
                for i in self.gaitOrder[1]:
                    if self.legArray[i - 1].legSide == "left":
                        self.legArray[i - 1].sendEvent(self.tf, 1, self.bus)
                    else:
                        self.legArray[i - 1].sendEventBack(self.tg, 0, self.bus)
                for i in self.gaitOrder[0]:
                    if self.legArray[i - 1].legSide == "left":
                        self.legArray[i - 1].sendEvent(self.tg, 0, self.bus)
                    else:
                        self.legArray[i - 1].sendEventBack(self.tf, 1, self.bus)

        elif self.speed == "jump":
            pass
            # jump for the giggles of it
        elif self.speed == "laydown" or (self.speed == 0 and self.direction == 5):
            if DEBUG:
                print("cpg: laying down")
            for Leg in self.legArray:
                Leg.lieDown(self.bus)
            time.sleep(2)

        elif self.speed == "stand_up" or (self.speed == 0 and self.direction == 0):
            if DEBUG:
                print("cpg: standing up")
            for Leg in self.legArray:
                Leg.standUp(self.bus)
            time.sleep(2)
            
        elif self.speed == "sit":
            if DEBUG:
                print("cpg: sitting")
            for i in [0,1]:
                self.legArray[i].standUp(self.bus)
            for i in range(2,6):
                self.legArray[i].lieDown(self.bus)
            time.sleep(2)
            
        elif self.speed == "bow":
            if DEBUG:
                print("cpg: bowing")
            for i in [4,5]:
                self.legArray[i].standUp(self.bus)
            for i in range(4):
                self.legArray[i].lieDown(self.bus)
            time.sleep(2)
            
    def Hopping(self):
        return np.matrix((1, 2, 3, 4, 5, 6))

    def Tripod(self):
        return np.array(((1, 4, 5), (2, 3, 6)))

    def Quadrapod(self):
        return np.array(((1, 6), (4, 5), (2, 3)))

    def ZebroGallop(self):
        return np.matrix(((1), (4, 5), (2, 3), (6)))

    def Pentapod(self):
        return np.array(((1), (2), (3), (4), (5), (6)))
