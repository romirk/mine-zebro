import threading
import module
import time
from datetime import datetime


# TODO define error messages and exceptions (use to implemented sanitation of inputs of methods in submodules array)
# TODO use disconnect function from the MCP to terminate a process that is taking too long
    # TODO implement timer to check if connection takes too long to respond
# TODO finish module ABC and loop method for connections

# responsible for sending/ receiving messages between MCP and the software modules
# only one module can communicate with the MCP throughout the bus at a time thus only one connection used
# Establishes connection between module(server) and MCP
class Router:

    #Private Variables only accessed by Router
    __sleep_interval = 3  # used by thread to sleep after seeing no command was given (in seconds)
    __is_connected = False
    __mcp_command = ""
    __server_id = ""

    #Public Variables
    output = "" #output data from modules read by MCP from here
    output_time = "" #time output variable has changed
    process_completed = False
    expecting_data = False
    is_error = False

    # Router errors
    __error_codes_to_messages = {
        1: 'connection disconnected by user',
        2: 'out of range index',
        3: 'module id does not exist',
        4: 'connection failed',
        5: 'module is already in list exist'
    }
        # error_messages_to_codes = dict((v, k) for k, v in error_codes_to_messages.iteritems())
        # print(error_codes_to_messages[3])
        # print(error_messages_to_codes['foo'])

    def __init__(self):
        self.__list = Submodules()  # list of submodules

    # Given a module by MCP add to submodules
    def add_module(self, module):
        if isinstance(module, module.__class__):
            self.__list.add_by_id(module.get_id(), module)

    # initialisation before entering listening loop
    def start(self):
        print("Router has started")
        self.__is_connected = False
        self.__listen_connections()

    # loop until command given by mcp (if no command sleep to an appropriate amount of time)
    def __listen_connections(self):
        while (True):
            # If no connection sleep
            if not self.__is_connected:
                time.sleep(self.__sleep_interval)
            else:
            # else we are expecting data by some module
                self.expecting_data = True
                self.process_completed = False
                module = self.__list.get_by_id(self.__server_id)

                # while connected and expecting data then output data to mpc (sleep to moderate loop)
                while self.__is_connected and self.expecting_data:
                    #TODO replace data with module output
                    self.send_to_mcp(data)
                    time.sleep(self.__sleep_interval)
                    # terminate connection
                self.disconnect()

    # used by message manager to establish connection
    def connect(self, id, command):
        self.__server_id = id
        self.__mcp_command = command
        self.__is_connected = True

    # terminates connection
    def disconnect(self):
        self.__server_id = ""
        self.__mcp_command = ""
        self.__is_connected = False
        return self.process_completed

    def send_to_mcp(self, data):
        self.output = data
        self.output_time = datetime.now().strftime("%H:%M:%S")



class Submodules:
    __predefined_max = 2  # should be equal to the max number of modules
    __id_list = ["com", "loco"]  # every module needs to implement a getter for their id
    size = 0

    # List of submodules that is stored by the router
    def __init__(self):
        self.__list = [-1] * self.__predefined_max

    def check_index(self, index):
        return (index <= self.__predefiend_max) and (index > 0)

    def check_id(self, id):
        return self.__list.__contains__(id)

    def is_in_list(self, module):
        return self.__list.__contains__(module)

    # Used for adding modules
    def map_id_to_index(self, id):
        self.check_id(id)
        return self.__id_list.index(id)

    def add_by_id(self, id, module):
        self.size += 1
        return self.add_by_index(self.map_id_to_index(id), module)

    def add_by_index(self, index, module):
        self.size += 1
        self.__list.insert(index, module)

    # Getters for modules
    def get_by_id(self, id):
        return self.__list[self.__mapidToIndex(id)]

    def get_by_index(self, index):
        return self.__list[index]
