import time

import cv2


# Getting camera access using python
# https://www.youtube.com/watch?v=ezAQvAN1xnQ

class CameraDummy:
    __sleep_interval = 0.5
    frame = ""
    vc = cv2.VideoCapture(0)

    def setup(self):
        return

    #gets a single frame from webcam
    def frame_capture(self):
        if self.vc.isOpened():#used to prevent crashing
            rval, self.frame = self.vc.read()
        else:
            rval = False

        return rval

    def get_frame(self):
        return self.frame

    #displays given frame
    def show_frame(self):
        while True:
            cv2.imshow("capture", self.frame) #show what is captured
            #rval, self.frame = self.vc.read() #update frame
            key = cv2.waitKey(20) #use escape to exit window
            if key == 27:
                break


if __name__ == '__main__':
    #Test method
    dummy = CameraDummy()
    #dummy.get_frames()
    if dummy.get_frame():
        print(dummy.frame)
        dummy.show_frame()

