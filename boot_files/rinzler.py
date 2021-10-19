import threading
import router
import comms

#class MCP:

# After boot rinzler must
# setup the router and critical modules : COMMS
if __name__ == "__main__":
    print("rinzler online")
    comms = comms.CommsManager()
    router = router.Router()

    # create and start Router thread
    routerThread = threading.Thread(target=router.boot_modules(comms))
    routerThread.start()

    #TODO start all other modules using this thread
    #locomotion = locopotion.locomotion_manager()

    # wait until all threads are done
    #routerThread.join()

    # both threads completely executed
    print("rinzler was defeated!")
