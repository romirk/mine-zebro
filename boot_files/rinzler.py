import threading
import router
import messageManager
import time
import commsApi
import commsDummy
import dummyModule
from datetime import datetime

#TODO implement hold flag
#TODO implement commands handled by MCP (terminate,shutdown)
#TODO check out multiprocessing module
# TODO access to this variables should be synchronous since used by 2 threads
# https://www.youtube.com/watch?v=rQTJuCCCLVo

#Boot precedure
# 1)setup router and critical modules (COMMS)
# 2)Create and start the router, cooms threads
# 3)Load all submodules to the Router
class Mcp:
    __sleep_interval = 1

    #setup all required objects and threads for execution
    def __init__(self):
        #initialise all objects
        self.router = router.Router()
        self.messenger = messageManager.MessageManager(commsDummy.CommsDummyManager())  # TODO change this to real Comms
        self.threads = list()
        self.isShutDown = False

        # create all locks
        comms_lock = threading.Lock()
        router_lock = threading.Lock()

        #setup threads and place in a list
        router_thread = threading.Thread(target=self.router.start,
                                         args=(router_lock, ))
        listen_to_user_thread = threading.Thread(target=self.messenger.listen_to_user,
                                         args=(comms_lock, ))
        in_out_thread = threading.Thread(target=self.input_output_loop,
                                         args=(comms_lock, router_lock))
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
            thread.start()
        return

    # loop that connects router and comms
    # locks are used to avoid deadlock
    # 2 locks: one for comms and one for router resources
    def input_output_loop(self, comms_lock, router_lock):
        while not self.isShutDown:
            comms_lock.acquire()
            if self.messenger.command_received:
                destination = self.messenger.get_destination()
                command = self.messenger.get_command()
                if destination == "mcp":
                    self.mcp_handle_command(command)
                else:
                    self.router.load_command(command, destination)
                self.messenger.command_received = False
            comms_lock.release()

            router_lock.acquire()
            if self.router.is_output_loaded:
                self.messenger.router_send_to_user(self.router.output, self.router.output_time,
                                            self.router.error, self.router.process_completed)
                self.router.is_output_loaded = False
            router_lock.release()

            time.sleep(self.__sleep_interval)
        return

    def mcp_handle_command(self,command):
        if command == "terminate":
            print("ehdkjflka")
        if command == "shutdown":
            self.messenger.mcp_send_to_user("shuttingDown", datetime.now().strftime("%H:%M:%S"))
            self.isShutDown = True
            self.router.is_shut_down = True
            self.messenger.is_shut_down = True

        return

if __name__ == "__main__":
    print("rinzler start")

    mcp = Mcp()
    mcp.start()

    # wait until all threads are done
    #routerThread.join()
    #listen_to_user_thread.join()
    #in_out_thread.join()
    # both threads completely executed

