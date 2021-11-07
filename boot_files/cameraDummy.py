import time
import cameraApi

import cv2


# abstractCamera implementation using computer webcam
# Getting camera access using python
# https://www.youtube.com/watch?v=ezAQvAN1xnQ

class CameraDummy(cameraApi.AbstractCamera):

    def setup(self):
        self.vc = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.frame = ""
        return

    #gets a single frame from webcam
    def frame_capture(self):
        if self.vc.isOpened():#used to prevent crashing
            rval, self.frame = self.vc.read()
        else:
            rval = False

        return rval

    #getter
    def get_frame(self):
        return self.frame

    #turn camera off
    def exit(self):
        self.vc.release()
        return

    #NOT used //displays given frame
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
    if dummy.frame_capture():
        print(dummy.frame)
        dummy.show_frame()

    dummy.exit()
    while True:
        time.sleep(1)

