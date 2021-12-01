import os
from datetime import datetime
from enum import Enum

import router
import module
import messageManager
import time
import communicationModule
import mcpHelper

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
        self.event = None

        self.internal_state = State.Running.value
        self.is_host_pc = is_host_pc

        # initialise all objects
        self.mcp_helper = mcpHelper.McpHelper(self)
        self.router = router.Router()
        #self.messenger = messageManager.MessageManager(communicationModule.CommunicationModule(), self.is_host_pc, self.event)  # TODO change this to real Comms
        self.messenger = messageManager.MessageManager(messageManager.CommsMock(), self.is_host_pc, self.event)

        # setup threads and place in a list
        self.threads = list()
        self.mcp_helper.setup_router_thread()
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

                elif self.router.is_command_loaded:
                    self.messenger.send_to_user_package(
                        messageManager.create_user_package(prefix,
                                                           datetime.now().strftime("%H:%M:%S"),
                                                           module.create_router_package(
                                                               module.OutputCode.error.value,
                                                               "Router command already executing, retry later"),
                                                           False))
                else:
                    self.router.load_command(prefix,command)

            # move package from router to message manager
            if self.router.is_package_loaded:
                self.router.lock.acquire()
                self.messenger.send_to_user_package(self.router.package)
                self.router.is_package_loaded = False
                self.router.lock.release()

            #check lights by Marijn
            self.mcp_helper.check_lights()

            #self.event.wait()
            #self.event.clear()
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
    mcp = Mcp(True)

    ##choose process creation method
    #if platform.system() == 'Windows':
    #    multiprocessing.set_start_method("spawn")
    #    mcp = Mcp(True)
    #else:
    #    multiprocessing.set_start_method("forkserver")
    #    mcp = Mcp(False)

    #start all non mcp threads
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
