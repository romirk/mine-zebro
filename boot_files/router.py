import threading
import module
import time
from datetime import datetime

#For MCP
# TODO use disconnect function from the MCP to terminate a process that is taking too long
# TODO implement timer to check if connection takes too long to respond

#For Router file here
# TODO define error messages and exceptions (use to implemented sanitation of inputs of methods in submodules array)
# TODO finish module ABC and loop method for connections

# responsible for sending/ receiving messages between MCP and the software modules
# only one module can communicate with the MCP throughout the bus at a time thus only one connection used
# Establishes connection between module(server) and MCP
class Router:

    #Private Variables only accessed by Router
    __sleep_interval = 3  # used by thread to sleep after seeing no command was given (in seconds)
    __is_command_loaded = False
    __mcp_command = ""
    __server_id = ""

    #Public Variables & Flags
    output = "" #output data from modules read by MCP from here
    output_time = "" #time output variable has changed
    error = "" #error message placed here
    process_completed = False
    is_output_loaded = False

    def __init__(self):
        self.__list = Submodules()  # list of submodules

    # initialisation before entering listening loop
    def start(self):
        print("Router has started")
        self.__listen_to_comms()

    # Given a module by MCP add to submodules
    def add_module(self, module):
        if isinstance(module, module.__class__):
            self.__list.add_by_id(module.get_id(), module)
            return
        raise Exception("Can't add non_module object to submodule list")

    # loop until command given by mcp (if no command sleep to an appropriate amount of time)
    def __listen_to_comms(self):
        while (True):
            # If no command to execute sleep
            if not self.__is_command_loaded:
                time.sleep(self.__sleep_interval)
            else:
            # else execute
                module = self.__list.get_by_id(self.__server_id)
                if not isinstance(module, module.__class__):
                    raise Exception("Failed to fetch module to execute command")
                self.__prepare()
                module.execute(self.__mcp_command);#blocking method
                self.__clean_up()

    #called before each command is executed
    def __prepare(self):
        self.process_completed = False
        self.output = ""
        self.output_time = ""
        self.error = ""
        self.is_output_loaded = False

    #called after each command is executed
    def __clean_up(self):
        self.__is_command_loaded = False
        self.__mcp_command = ""
        self.__server_id = ""
        self.process_completed = True

    #called by active module to return data to mcp
    def send_data_to_mcp(self, output, error):
        self.is_output_loaded = True
        self.output = output
        self.output_time = datetime.now().strftime("%H:%M:%S")
        self.error = error

    #called by mcp to load a command to be executed
    def load_command(self, command, id):
        self.__mcp_command = command
        self.__server_id = id
        self.__is_command_loaded = True



class Submodules:
    __id_list = ["com", "loco", "Dummy"]  # every module needs to implement a getter for their id
    __predefined_max = len(__id_list)  # should be equal to the max number of modules
    size = 0

    # List of submodules that is stored by the router
    def __init__(self):
        self.__list = [-1] * self.__predefined_max

    def check_id(self, id):
        return self.__id_list.__contains__(id)

    def is_in_list(self, module):
        return self.__list.__contains__(module)

    # Used for adding modules
    def map_id_to_index(self, id):
        if self.check_id(id):
            return self.__id_list.index(id)
        raise Exception("Submodule list: id <" + id + "> does not exist")

    def add_by_id(self, id, module):
        index = self.map_id_to_index(id)
        if not self.is_in_list(module):
            self.size += 1
            return self.__list.insert(index, module)
        else:
            raise Exception ("Submodule list: Module is already loaded of given id")

    # Getter for modules
    def get_by_id(self, id):
        return self.__list[self.__mapidToIndex(id)]
