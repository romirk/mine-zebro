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

def input_output_loop(router, messenger, comms_lock, router_lock):
    #loop for forwarding messages between submodules and user
    while True:
        comms_lock.acquire()
        if messenger.command_received:
            router.load_command(messenger.get_command(), messenger.get_destination())
            messenger.command_received = False
        comms_lock.release()

        router_lock.acquire()
        if router.is_output_loaded:
            messenger.send_to_user(router.output, router.output_time, router.error, router.process_completed)
            router.is_output_loaded = False
        router_lock.release()

        time.sleep(2)

if __name__ == "__main__":
    print("rinzler start")

    #setup
    router = router.Router()
    messenger = messageManager.MessageManager(commsDummy.CommsDummyManager()) #TODO change this to real Comms

    # setup Router,Comms thread

    comms_lock = threading.Lock()
    router_lock = threading.Lock()
    routerThread = threading.Thread(target=router.start, args=(router_lock,))
    listen_to_user_thread = threading.Thread(target=messenger.listen_to_user, args=(comms_lock,))
    in_out_thread = threading.Thread(target=input_output_loop, args=(router, messenger, comms_lock, router_lock))

    #TODO start all other modules here
    dummyModule = dummyModule.DummyManager()
    router.add_module(dummyModule)

    #start threads
    routerThread.start()
    listen_to_user_thread.start()
    in_out_thread.start()

    print("Main thread continuous")


    # wait until all threads are done
    routerThread.join()
    listen_to_user_thread.join()
    in_out_thread.join()
    # both threads completely executed
    print("return 0")

