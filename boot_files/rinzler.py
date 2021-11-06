import os
import sys
import threading
from enum import Enum

import router
import messageManager
import time
import commsApi
import commsDummy
import mcpHelper
import dummyModule
from datetime import datetime


# python passes immutable objects by copying

# TODO Replace exceptions with couts to user
# TODO define error messages and exceptions (use to implemented sanitation of inputs of methods in submodules array)
# https://www.youtube.com/watch?v=rQTJuCCCLVo
# TODO autonomous checking of battery status
# TODO autonomous checking for overheating motors
# TODO add camera
# For MCP
# TODO use disconnect function from the MCP to terminate a process that is taking too long
# TODO implement timer to check if connection takes too long to respond


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

        # setup threads and place in a list
        self.threads = list()
        self.mcp_helper.setup_router_thread()
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
    # 2 locks: one for comms and one for router resources
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



