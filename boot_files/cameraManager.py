import copy
import threading
from datetime import datetime

import messageManager

import time

# Wrapper for the camera that forwards frames from camera to mcp
# Similar logic to messageManager
from boot_files import cameraApi, cameraDummy


class CameraManager:
    is_shut_down = True  # TODO turn False if camera must start on startup
    time_between_frames = 5  # in seconds
    # variables shared between threads that need locks to write on are:
    __frame_number = 0  # idenitfier used to keep track of frames python3 has no upper limit for integers

    def __init__(self, camera: cameraApi.AbstractCamera,
                 is_package_ready, time_between_frames, package, is_shut_down) -> None:
        self.__lock = threading.Lock()

        self.__camera = camera
        self.is_camera_package_ready = is_package_ready
        self.time_between_frames = time_between_frames
        self.__camera_package = package
        self.is_shut_down = is_shut_down

    # main loop that retrives frames
    def listen_to_camera(self) -> None:
        self.__camera.setup()
        while not bool(self.is_shut_down.value):
            frame = self.__get_valid_input()
            self.__set_frame(frame)
            time.sleep(self.time_between_frames.value)
        self.__camera.exit()
        return

    # Get valid input from the camera (check for crashes or errors)
    def __get_valid_input(self) -> []:
        if self.__camera.frame_capture():
            return self.__camera.get_frame()
        else:
            return []

    # create the package for the mcp thread to send to comms
    def __set_frame(self, frame: list) -> None:
        self.__lock.acquire()
        has_process_completed = True
        if len(frame) == 0:
            has_process_completed = False
        command_id = "frame " + str(self.__frame_number)

        self.__camera_package["command_id"] = command_id
        self.__camera_package["timestamp"] = datetime.now().strftime("%H:%M:%S")
        self.__camera_package["package"]  = frame
        self.__camera_package["has_process_complete"] = has_process_completed

        self.is_camera_package_ready.value = 1
        self.__frame_number += 1
        self.__lock.release()


def start(is_package_ready, time_between_frames, package, is_shut_down):
    camera_manager = CameraManager(cameraDummy.CameraDummy(),
                                   is_package_ready,
                                   time_between_frames,
                                   package,
                                   is_shut_down)
    camera_manager.listen_to_camera()
    return
