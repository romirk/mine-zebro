import threading
import router
import messageManager
import time
import commsApi
import commsDummy
import dummyModule

#TODO using 2 comms thread for monitoring user input and outputing stuff learn about locks
#TODO implement hold flag

#Boot precedure
# 1)setup router and critical modules (COMMS)
# 2)Create and start the router, cooms threads
# 3)Load all submodules to the Router
class Mcp:

    #setup all required objects and threads for execution
    def __init__(self):
        #initialise all objects
        self.router = router.Router()
        self.messenger = messageManager.MessageManager(commsDummy.CommsDummyManager())  # TODO change this to real Comms
        self.threads = list()

        # create all locks
        comms_lock = threading.Lock()
        router_lock = threading.Lock()

        #setup threads and place in a list
        router_thread = threading.Thread(target=self.router.start, args=(router_lock,))
        listen_to_user_thread = threading.Thread(target=self.messenger.listen_to_user, args=(comms_lock,))
        in_out_thread = threading.Thread(target=self.input_output_loop, args=(self.router, self.messenger, comms_lock, router_lock))
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
    def input_output_loop(self,router, messenger, comms_lock, router_lock):
        while True:
            comms_lock.acquire()
            if messenger.command_received:
                destination = messenger.get_destination()
                command = messenger.get_command()
                if (destination == "mcp"):
                    self.mcp_handle_command(command)
                else:
                    router.load_command(command, destination)
                messenger.command_received = False
            comms_lock.release()

            router_lock.acquire()
            if router.is_output_loaded:
                messenger.send_to_user(router.output, router.output_time, router.error, router.process_completed)
                router.is_output_loaded = False
            router_lock.release()

            time.sleep(2)

    def mcp_handle_command(self,command):
        if command == "terminate":
            print("ehdkjflka")
            #for i in self.threads:

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

