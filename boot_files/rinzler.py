import multiprocessing
import os
import platform
from datetime import datetime
from enum import Enum

from router import Str
import router
import module
import messageManager
import time
import commsApi
import communicationModule
import mcpHelper
import cameraManager
import cameraDummy

#tries to import lights so it detects if the host is a rover or pc
try:
    from leds import LEDs
except:
    LEDs = int


# TODO use this for regular commms socket.emit('command', {command: 'dummy count'});


# Boot procedure
# 1)setup all essential objects (router,messenger,camera,mcp_helper)
# 2)setup all threads and place then in a list
# 3)start all threads
class Mcp:
    __sleep_interval = 1

    # setup all required objects and threads for execution
    def __init__(self, is_host_pc) -> None:
        self.routerLock = None
        self.internal_state = State.Running.value
        self.is_host_pc = is_host_pc

        # shared router variables
        self.router_data = None

        # initialise all objects
        self.mcp_helper = mcpHelper.McpHelper(self)
        #self.messenger = messageManager.MessageManager(communicationModule.CommunicationModule())  # TODO change this to real Comms
        self.messenger = messageManager.MessageManager(messageManager.CommsMock(), self.is_host_pc)
        self.cameraManager = cameraManager.CameraManager(cameraDummy.CameraDummy(),
                                                         self.messenger)  # TODO change this to real Camera

        # setup threads and place in a list
        self.threads = list()
        self.mcp_helper.setup_router_thread()
        self.mcp_helper.setup_camera_thread()
        self.mcp_helper.setup_non_restartable_threads()
        return

    # start all threads
    def start(self) -> None:
        for thread in self.threads:
            thread.daemon = True
            thread.start()
        return

    # locks are used to avoid deadlock when accessing shared variables
    def mcp_loop(self) -> None:
        while self.internal_state == State.Running.value:

            if self.messenger.input_received:
                # get split input (prefix/destination)
                prefix = self.messenger.get_destination()
                command = self.messenger.get_command()
                self.messenger.reset_input_received()

                # move input from message manager to router iff no input loaded or handle if mcp command
                if prefix.startswith("mcp"):
                    self.mcp_helper.handle_command(prefix, command)

                elif self.router_data[Str.is_command_loaded.value]:
                    self.messenger.send_to_user_package(
                        messageManager.create_user_package(prefix,
                                                           datetime.now().strftime("%H:%M:%S"),
                                                           module.create_router_package(
                                                               module.OutputCode.error.value,
                                                               "Router command already executing, retry later"),
                                                           False))
                else:
                    self.routerLock.acquire()
                    self.router_data[Str.command.value] = command
                    self.router_data[Str.prefix.value] = prefix
                    self.router_data[Str.command.value] = command
                    self.router_data[Str.is_command_loaded.value] = True
                    self.routerLock.release()

            # move package from router to message manager
            if self.router_data[Str.is_package_ready.value]:
                self.routerLock.acquire()
                self.messenger.send_to_user_package(self.router_data[Str.package.value])
                self.router_data[Str.is_package_ready.value] = False
                self.routerLock.release()

            self.mcp_helper.check_lights()

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

    #choose process creation method
    if platform.system() == 'Windows':
        multiprocessing.set_start_method("spawn")
        mcp = Mcp(True)
    else:
        multiprocessing.set_start_method("forkserver")
        mcp = Mcp(False)
    mcp.start()
    # wait a bit for all threads to start just to be safe
    time.sleep(1)

    # start mcp loop
    mcp.mcp_loop()

    # wait for all threads to finish to shutdown safely
    if mcp.internal_state == State.ShutDown.value or mcp.internal_state == State.Restart.value:
        mcp.wait()

    # command given to the terminal to restart __main__
    if mcp.internal_state == State.Restart.value:
        os.system("Python rinzler.py")
