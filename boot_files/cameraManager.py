import copy
import threading


import time


# Wrapper for the camera that forwards frames from camera to mcp
# Similar logic to messageManager
class CameraManager:
    is_shut_down = True
    time_between_frames = 5 #in seconds
    # variables shared between threads that need locks to write on are:
    __stored_frame = ""
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

    # store given frame as object attribute
    def __set_frame(self, frame):
        self.__lock.acquire()
        self.__stored_frame = frame
        self.frame_ready = True
        self.__lock.release()

    def reset_frame_ready(self):
        self.__lock.acquire()
        self.frame_ready = False
        self.__lock.release()

    # getter for frames
    def get_frame(self):
        self.__lock.acquire()
        frame = copy.deepcopy(self.__stored_frame)
        self.__lock.release()
        return frame
