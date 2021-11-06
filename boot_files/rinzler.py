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
        # create all locks
        message_manager_lock = threading.Lock()
        router_lock = threading.Lock()

        # initialise all objects
        self.mcp_command_handler = mcpHelper.McpCommandHandler(self)
        self.router = router.Router(router_lock)
        self.messenger = messageManager.MessageManager(commsDummy.CommsDummyManager(),
                                                       message_manager_lock)  # TODO change this to real Comms
        self.threads = list()
        self.internal_state = State.Running

        # setup threads and place in a list
        router_thread = threading.Thread(target=self.router.start)
        listen_to_user_thread = threading.Thread(target=self.messenger.listen_to_user)
        in_out_thread = threading.Thread(target=self.input_output_loop,
                                         args=(router_lock,))
        router_thread.setName("RouterThread")
        listen_to_user_thread.setName("UserInputThread")
        in_out_thread.setName("In/OutThread")
        self.threads.append(router_thread)
        self.threads.append(listen_to_user_thread)
        self.threads.append(in_out_thread)

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
    def input_output_loop(self, router_lock):
        while not self.internal_state == State.ShutDown:
            # moves input from message manager to router
            if self.messenger.input_received:
                destination = self.messenger.get_destination()
                command = self.messenger.get_command()
                self.messenger.reset_input_received()
                if destination == "mcp":
                    self.mcp_command_handler.execute(command)
                else:
                    self.router.load_command(command, destination)

            if self.router.is_output_loaded:
                router_lock.acquire()
                self.messenger.send_to_user_package(self.router.output, self.router.output_time, self.router.error,
                                                    self.router.process_completed)
                self.router.is_output_loaded = False
                router_lock.release()

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


if __name__ == "__main__":
    print("rinzler start")

    mcp = Mcp()
    mcp.start()

    while mcp.internal_state == State.Running:
        time.sleep(1)

    if mcp.internal_state == State.ShutDown:
        mcp.wait()


