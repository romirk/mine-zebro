import threading
import comms
import time

#TODO define error messages and exceptions

class Router:
    __interval = 3 #used by thread to sleep after seeing no command was given (in seconds)
    mcp_command = ""

    # responsible for sending/ receiving messages between MCP and the software modules
    def __init__(self):
        self.__list = Submodules() #list of submodules
        self.mcp_command = ""            #mcp commands read from here

    # initialisation before entering listening loop
    def start(self):
        print("Router has started")
        self.listen_Commands()

    #loop until command given by mcp
    #if no command sleep to an appropriate amount of time
    def listen_Commands(self):
        while(True):
            # Detects command from MCP
            if self.mcp_command != "":
                #TODO execute command

                print("hello")

                #reset the command string
                self.mcp_command = ""
            else:
                time.sleep(self.__interval)

    #Given a non-essential module by MCP add to submodules
    def add_module(self, module):
        self.__list.add_by_id(module.get_id(), module)

    #def send_to_module(self, module, data):
        #TODO


    #def send_to_mcp(self, data):
        #TODO


class Submodules:
    __predefined_max = 2 # should be equal to the max number of modules
    __id_list = ["Comms", "locomotion"] #every module needs to implement a getter for their id
    size = 0

#List of submodules that is stored by the router
    def __init__(self):
        self.__list = [-1] * self.__predefined_max

    #TODO input sanitation not implemented yet
    def check_index(self,index):
        return (index <= self.__predefiend_max) and (index > 0)

    def check_id(self,id):
        return self.__list.__contains__(id)

    def is_in_list(self, module):
        return self.__list.__contains__(module)

    #Used for adding modules
    def map_id_to_index(self, id):
        self.check_id(id)
        return self.__id_list.index(id)

    def add_by_id(self, id, module):
        self.size += 1
        return self.add_by_index(self.map_id_to_index(id), module)

    def add_by_index(self, index, module):
        self.size += 1
        self.__list.insert(index, module)

    #Getters for modules
    def get_by_id(self, id):
        return self.__list.index(id)

    def get_by_index(self, index):
        return self.__list[index]
