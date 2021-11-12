import os
from datetime import datetime
from enum import Enum

import router
import module
import messageManager
import time
import commsApi
import communicationModule
import mcpHelper
import cameraManager
import cameraDummy


# TODO define error messages and exceptions for submodules
# TODO replace threading router thread with a process (geekfreak multiprocessing)
# TODO open different terminal for output and input
# TOD socket.emit('command', {command: 'dummy count'});

# Processing router: Keep it on hold

# Boot procedure
# 1)setup all essential objects (router,messenger,camera,mcp_helper)
# 2)setup all threads and place then in a list
# 3)start all threads
class Mcp:
    __sleep_interval = 1
    # __status_sleep_interval = 0.5  # how often to check motors for overheating and battery
    __status_sleep_interval = 0  # for now use zero so not to check the battery or the motors

    # setup all required objects and threads for execution
    def __init__(self) -> None:
        self.internal_state = State.Running.value

        # initialise all objects
        self.mcp_helper = mcpHelper.McpHelper(self)
        self.router = router.Router()
        self.messenger = messageManager.MessageManager(messageManager.CommsMock())  # TODO change this to real Comms
        self.cameraManager = cameraManager.CameraManager(cameraDummy.CameraDummy(), self.messenger)  # TODO change this to real Camera

        # setup threads and place in a list
        self.threads = list()
        self.mcp_helper.setup_router_thread()
        self.mcp_helper.setup_camera_thread()
        self.mcp_helper.setup_non_restartable_threads(self.__status_sleep_interval)
        return

    # start all threads
    def start(self) -> None:
        for thread in self.threads:
            thread.daemon = True
            thread.start()
        return

    # locks are used to avoid deadlock when accessing shared variables
    def input_output_loop(self) -> None:
        while self.internal_state == State.Running.value:

            # move input from message manager to router or handle if mcp command
            if self.messenger.input_received:
                prefix = self.messenger.get_destination()
                command = self.messenger.get_command()
                self.messenger.reset_input_received()
                if prefix.startswith("mcp"):
                    self.mcp_helper.handle_command(prefix, command)
                else:
                    if self.router.is_command_loaded:
                        self.messenger.send_to_user_package(
                            messageManager.create_user_package(prefix,
                                                               datetime.now().strftime("%H:%M:%S"),
                                                               module.create_router_package(
                                                                   module.OutputCode.error.value,
                                                                   "Command already loaded"),
                                                               False))
                    else:
                        self.router.load_command(prefix, command)

            # move package from router to message manager
            if self.router.is_package_loaded:
                self.router.lock.acquire()
                self.messenger.send_to_user_package(self.router.package)
                self.router.is_package_loaded = False
                self.router.lock.release()

            # moves frame from cameraManager to user
            #if self.cameraManager.frame_ready:
            #    package = self.cameraManager.get_package()
            #    self.cameraManager.reset_frame_ready()
            #    self.messenger.send_to_user_package(package)

            time.sleep(self.__sleep_interval)
        return

    # wait for all threads to finish before shutdown
    def wait(self) -> None:
        for thread in self.threads:
            thread.join()
        return


# Class shows all internal states mcp can be active in
class State(Enum):
    Running = 0
    ShutDown = 1
    Terminate = 2
    Restart = 3


if __name__ == "__main__":
    print("\nRINZLER STARTED")

    mcp = Mcp()
    mcp.start()

    # keep main thread busy until state changes
    while mcp.internal_state == State.Running.value:
        time.sleep(1)

    # wait for all threads to finish to shutdown safely
    if mcp.internal_state == State.ShutDown.value or mcp.internal_state == State.Restart.value:
        mcp.wait()

    # command given to the terminal to restart __main__
    if mcp.internal_state == State.Restart.value:
        os.system("Python rinzler.py")
