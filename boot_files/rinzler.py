import threading
import router
import messageManager
import time
import comms
import dummyModule


#Boot precedure
# 1)setup router and critical modules (COMMS)
# 2)Create and start the router, cooms threads
# 3)Load all submodules to the Router
if __name__ == "__main__":
    print("rinzler start")

    #setup
    router = router.Router()
    #cooms = comms.CommsManager()

    # create and start Router,Cooms thread
    routerThread = threading.Thread(target=router.start, args=())
    routerThread.start()
    #coomsThread = threading.Thread(target=router.start, args=())
    #coomsThread.start()

    #TODO start all other modules using this thread
    print("Other thread continuous")
    dummyModule = dummyModule.DummyManager()
    router.add_module(dummyModule)

    #messenger = messageManager.MessageManager(router)

    while(True):
        time.sleep(2)
        router.mcp_command = "bob"





    # wait until all threads are done
    routerThread.join()
    # both threads completely executed
    print("return 0")
