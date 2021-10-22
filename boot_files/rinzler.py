import threading
import router
import messageManager
import time
import comms


#Boot precedure
# 1)setup router and critical modules : (ex:COMMS)
# 2)Create and start the router thread
if __name__ == "__main__":
    print("rinzler online")

    router = router.Router()
    module = comms.CommsManager()
    router.add_module(module)

    # create and start Router thread
    routerThread = threading.Thread(target=router.start, args=())
    routerThread.start()

    #TODO start all other modules using this thread
    #locomotion = locopotion.locomotion_manager()
    #router.add_module(locomotion)

    print("Other thread continuous")
    messenger = messageManager.MessageManager(router)

    while(True):
        time.sleep(2)
        router.mcp_command = "bob"





    # wait until all threads are done
    routerThread.join()
    # both threads completely executed
    print("return 0")
