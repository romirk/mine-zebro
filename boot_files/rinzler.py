import threading
import router
import messageManager
import time
import commsApi
import commsDummy
import dummyModule


#Boot precedure
# 1)setup router and critical modules (COMMS)
# 2)Create and start the router, cooms threads
# 3)Load all submodules to the Router
if __name__ == "__main__":
    print("rinzler start")

    #setup
    router = router.Router()
    #pass commsApi instance
    messenger = messageManager.MessageManager(commsDummy.CommsDummyManager())

    # create and start Router,Comms thread
    routerThread = threading.Thread(target=router.start, args=())
    routerThread.start()
    messenger.start()

    #TODO start all other modules using this thread
    print("Other thread continuous")
    dummyModule = dummyModule.DummyManager()
    router.add_module(dummyModule)


    #loop for forwarding messages between submodules and user
    while True:
        if messenger.command_received:
            router.load_command(messenger.get_command(),messenger.get_destination())
            messenger.command_received = False
        if router.is_output_loaded:
            messenger.send_to_user(router.output, router.output_time, router.error, router.process_completed)
        time.sleep(2)


    # wait until all threads are done
    routerThread.join()
    # both threads completely executed
    print("return 0")
