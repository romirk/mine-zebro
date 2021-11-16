import copy
import threading
import messageManager
from datetime import datetime

import messageManager

import time

# Wrapper for the camera that forwards frames from camera to mcp
# Similar logic to messageManager
import cameraApi


class CameraManager:
    is_shut_down = True  # TODO turn False if camera must start on startup
    time_between_frames = 0.1  # in seconds
    # variables shared between threads that need locks to write on are:
    __stored_frame = {}
    __frame_number = 0  # idenitfier used to keep track of frames python3 has no upper limit for integers
    frame_ready = False

    def __init__(self, camera: cameraApi.AbstractCamera, message_manager: messageManager) -> None:
        self.__camera = camera
        self.__lock = threading.Lock()
        self.__message_manager = message_manager

    # main loop that retrives frames
    def listen_to_camera(self) -> None:
        self.__camera.setup()
        while not self.is_shut_down:
            frame = self.__get_valid_input()
            self.__set_frame(frame)
            self.send_to_user()
            time.sleep(self.time_between_frames)
        self.__camera.exit()
        return

    # Get valid input from the camera (check for crashes or errors)
    def __get_valid_input(self) -> []:
        if self.__camera.frame_capture():
            return self.__camera.get_frame()
        else:
            return []

    # create the package for the mcp thread to send to comms
    def __set_frame(self, frame) -> None:
        self.__lock.acquire()
        is_process_complete = True
        if len(frame) == 0:
            is_process_complete = False
        command_id = "frame " + str(self.__frame_number)
        self.__stored_frame = messageManager.create_user_package(command_id,
                                                                 datetime.now().strftime("%H:%M:%S"),
                                                                 #"frame received", #TODO replace with frame
                                                                 frame.tolist(),
                                                                 is_process_complete)
        self.frame_ready = True
        self.__frame_number += 1
        self.__lock.release()

    def reset_frame_ready(self) -> None:
        self.__lock.acquire()
        self.frame_ready = False
        self.__lock.release()

    # getter for frames
    def send_to_user(self) -> None:
        self.__lock.acquire()
        self.__message_manager.send_to_user_package(self.__stored_frame)
        self.__lock.release()
