import threading
import router
import messageManager
import time
import commsApi
import commsDummy
import dummyModule
from datetime import datetime

#python passes immutable objects by copying

# TODO implement commands handled by MCP (terminate,shutdown)
# TODO create enums for shutdown and terminate
# TODO Create method that check if command exist in a module
# https://www.youtube.com/watch?v=rQTJuCCCLVo

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
        self.router = router.Router(router_lock)
        self.messenger = messageManager.MessageManager(commsDummy.CommsDummyManager(), message_manager_lock)  # TODO change this to real Comms
        self.threads = list()
        self.isShutDown = False


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

        # TODO start all other modules here
        self.router.add_module(dummyModule.DummyManager())
        return

    # start all threads
    def start(self):
        for thread in self.threads:
            thread.daemon = True
            thread.start()
        return

    # loop that connects router and comms
    # locks are used to avoid deadlock
    # 2 locks: one for comms and one for router resources
    def input_output_loop(self, router_lock):
        while not self.isShutDown:
            #moves input from message manager to router
            if self.messenger.input_received:
                destination = self.messenger.get_destination()
                command = self.messenger.get_command()
                self.messenger.reset_input_received()
                if destination == "mcp":
                    self.mcp_handle_command(command)
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

    def mcp_handle_command(self, command):
        if command == "terminate":
            self.messenger.is_shut_down = True
            self.isShutDown = True
        elif command == "shutdown":
            self.messenger.send_to_user_package("shuttingDown", datetime.now().strftime("%H:%M:%S"), 0, True)
            self.router.is_shut_down = True
            self.messenger.is_shut_down = True
            self.isShutDown = True
        elif command == "hold":
            self.router.hold_module_execution = True

        return


if __name__ == "__main__":
    print("rinzler start")

    mcp = Mcp()
    mcp.start()

    while not mcp.isShutDown:
        time.sleep(1)

#shared variables
#messageManager
#