import os
from datetime import datetime
from enum import Enum

import router
import messageManager
import time
import commsApi
import commsDummy
import mcpHelper
import dummyModule
import cameraManager
import cameraDummy


# python passes immutable objects by copying

# TODO define error messages and exceptions (use to implemented sanitation of inputs of methods in submodules array)
# https://www.youtube.com/watch?v=rQTJuCCCLVo
# TODO autonomous checking of battery status & overheating motors
# TODO add camera
# TODO be able to restart camera and router processes
# TODO replace threading with processing


# Boot precedure
# 1)setup router and critical modules (COMMS)
# 2)Create and start the router, cooms threads
# 3)Load all submodules to the Router
class Mcp:
    __sleep_interval = 1

    # setup all required objects and threads for execution
    def __init__(self):
        self.internal_state = State.Running.value

        # initialise all objects
        self.mcp_helper = mcpHelper.McpHelper(self)
        self.router = router.Router()
        self.messenger = messageManager.MessageManager(commsDummy.CommsDummyManager())  # TODO change this to real Comms
        self.cameraManager = cameraManager.CameraManager(cameraDummy.CameraDummy())  # TODO change this to real Camera

        # setup threads and place in a list
        self.threads = list()
        self.mcp_helper.setup_router_thread()
        self.mcp_helper.setup_camera_thread()
        self.mcp_helper.setup_non_restartable_threads()

        self.add_modules_to_router()
        return

    def add_modules_to_router(self):
        # TODO start all other modules here
        self.router.add_module(dummyModule.DummyManager())
        return

    # start all threads
    def start(self):
        for thread in self.threads:
            thread.daemon = True
            thread.start()
        return

    # locks are used to avoid deadlock
    # 3 locks: messageManager,router,cameraManager
    def input_output_loop(self):
        while self.internal_state == State.Running.value:
            # moves input from message manager to router
            if self.messenger.input_received:
                destination = self.messenger.get_destination()
                command = self.messenger.get_command()
                self.messenger.reset_input_received()
                if destination == "mcp":
                    self.mcp_helper.handle_command(command)
                else:
                    self.router.load_command(command, destination)

            # movies output from router to the message manager
            if self.router.is_output_loaded:
                self.router.lock.acquire()
                self.messenger.send_to_user_package(self.router.output, self.router.output_time, self.router.error,
                                                    self.router.process_completed)
                self.router.is_output_loaded = False
                self.router.lock.release()

            # moves frame from cameraManager to user
            if self.cameraManager.frame_ready:
                frame = self.cameraManager.get_frame()
                self.cameraManager.reset_frame_ready()
                if len(frame) == 0:
                    self.messenger.send_to_user_text("Frame could not be received")
                else:
                    self.messenger.send_to_user_text("Frame received time: " + datetime.now().strftime("%H:%M:%S")) #TODO replace with actual frame (str(frame))

            time.sleep(self.__sleep_interval)
        return

    # wait for all threads
    def wait(self):
        for thread in self.threads:
            thread.join()
        return


class State(Enum):
    Running = 0
    ShutDown = 1
    Terminate = 2
    Restart = 3


if __name__ == "__main__":
    print("rinzler start")

    mcp = Mcp()
    mcp.start()

    while mcp.internal_state == State.Running.value:
        time.sleep(1)

    if mcp.internal_state == State.ShutDown.value or mcp.internal_state == State.Restart.value:
        mcp.wait()

    if mcp.internal_state == State.Restart.value:
        #TODO check stackoverflow why it works only in debug https://stackoverflow.com/questions/69864001/python-file-that-recursively-executes-itself
        #os.execv(sys.executable, [sys.executable, __file__] + sys.argv)
        os.system("Python rinzler.py")



