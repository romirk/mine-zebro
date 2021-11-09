import copy
import threading
from datetime import datetime

import messageManager


import time


# Wrapper for the camera that forwards frames from camera to mcp
# Similar logic to messageManager
class CameraManager:
    is_shut_down = True #TODO turn False if camera must start on startup
    time_between_frames = 5 #in seconds
    # variables shared between threads that need locks to write on are:
    __stored_frame = {}
    __frame_number = 0 #idenitfier used to keep track of frames python3 has no upper limit for integers
    frame_ready = False

    def __init__(self, camera):
        self.__camera = camera
        self.__lock = threading.Lock()

    #main loop that retrives frames
    def listen_to_camera(self):
        self.__camera.setup()
        while not self.is_shut_down:
            frame = self.__get_valid_input()
            self.__set_frame(frame)
            time.sleep(self.time_between_frames)
        self.__camera.exit()
        return

    # Get valid input from the camera (check for crashes or errors)
    def __get_valid_input(self):
        if self.__camera.frame_capture():
            return self.__camera.get_frame()
        else:
            return []

    # create the package for the mcp thread to send to comms
    def __set_frame(self, frame):
        self.__lock.acquire()
        is_process_complete = True
        if len(frame) == 0:
            is_process_complete = False
        command_id = "frame " + str(self.__frame_number)
        self.__stored_frame = messageManager.create_package(command_id,
                                                            frame,
                                                            datetime.now().strftime("%H:%M:%S"),
                                                            is_process_complete)
        self.frame_ready = True
        self.__frame_number += 1
        self.__lock.release()

    def reset_frame_ready(self):
        self.__lock.acquire()
        self.frame_ready = False
        self.__lock.release()

    # getter for frames
    def get_package(self):
        self.__lock.acquire()
        frame = copy.deepcopy(self.__stored_frame)
        self.__lock.release()
        return frame
