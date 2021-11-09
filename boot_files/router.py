import threading
from typing import List

import dummyModule
import messageManager
import module
import time
from datetime import datetime


# responsible for sending/ receiving messages between MCP and the submodules
# only one module can communicate with the MCP throughout the bus at a time thus only one connection used
# Establishes connection between module(server) and MCP
class Router:
    # Private Variables only accessed by Router
    __sleep_interval = 3  # used by thread to sleep after seeing no command was given (in seconds)
    __command = ""
    __prefix = ""

    # Public Variables & Flags
    package = ""  # package data from modules read by MCP from here
    is_command_loaded = False
    is_package_loaded = False
    is_shut_down = False
    halt_module_execution = False

    def __init__(self):
        self.__list = Submodules()  # list of submodules
        self.lock = threading.Lock()

    # initialisation before entering listening loop
    def start(self):
        self.__clean_up()
        self.__prepare()
        self.is_shut_down = False
        self.__setup_all_modules()
        self.__listen_to_commands()

    # Given a module by MCP add to submodules list
    def __add_module(self, module):
        if isinstance(module, module.__class__):
            self.__list.add_by_id(module.get_id(), module)
            return
        raise Exception("Can't add non_module object to submodule list")

    # Use this method to add all modules to the current router instance
    def __setup_all_modules(self):
        # TODO start all other modules here
        self.__add_module(dummyModule.DummyManager(self))

        self.__list.setup()  # calls setup method in each module
        return

    # loop until command given by mcp (if no command sleep to an appropriate amount of time)
    def __listen_to_commands(self):
        while not self.is_shut_down:
            # If no command to execute sleep
            if not self.is_command_loaded:
                time.sleep(self.__sleep_interval)
            else:
                # else execute
                server_id = "".join(
                    [i for i in self.__prefix if not i.isdigit()])  # remove identifier which is a number
                if not self.__list.check_id(server_id):
                    self.send_package_to_mcp("Router:Failed to fetch module with id: " + str(server_id), False)
                    self.__clean_up()
                else:
                    module = self.__list.get_by_id(server_id)
                    self.__prepare()
                    module.execute(self.__command)  # blocking method
                    self.send_package_to_mcp("", True)
                    self.__clean_up()

    # Note: All functions that change attributes need to use lock to avoid deadlock
    # called before each command is executed
    def __prepare(self):
        self.lock.acquire()
        self.package = ""
        self.halt_module_execution = False
        self.lock.release()

    # called after each command is executed
    def __clean_up(self):
        self.lock.acquire()
        self.is_command_loaded = False
        self.__command = ""
        self.__prefix = ""
        self.lock.release()

    # called by active module to return data to mcp
    def send_package_to_mcp(self, module_output, has_process_completed):
        while self.is_package_loaded:
            time.sleep(1)
        self.lock.acquire()

        self.package = messageManager.create_user_package(self.__prefix, module_output,
                                                          datetime.now().strftime("%H:%M:%S"), has_process_completed)
        self.is_package_loaded = True
        self.lock.release()

    # called by mcp to load a command to be executed
    def load_command(self, prefix, command):
        self.lock.acquire()
        self.__command = command
        self.__prefix = prefix
        self.is_command_loaded = True
        self.lock.release()

    # Use this method to remove all modules from the list
    def clear_modules_list(self):
        self.__list.clear()
        return


# list of submodules contained in the router
class Submodules:
    __id_list = ["com", "loco", "dummy"]  # every module needs to implement a getter for their id
    __predefined_max = len(__id_list)  # should be equal to the max number of modules
    __size = 0

    # List of submodules that is stored by the router
    def __init__(self):
        self.__list = [-1] * self.__predefined_max

    def setup(self):
        for i in range(self.__predefined_max):
            obj = self.__list.__getitem__(i)
            if isinstance(obj, module.Module.__class__):
                obj.setup()

    def check_id(self, id):
        return self.__id_list.__contains__(id)

    def is_in_list(self, module):
        return self.__list.__contains__(module)

    # Used for adding modules
    def __map_id_to_index(self, id):
        if self.check_id(id):
            return self.__id_list.index(id)
        raise Exception("Submodule list: id <" + id + "> does not exist")

    def add_by_id(self, id, module):
        index = self.__map_id_to_index(id)
        if not self.is_in_list(module):
            self.__size += 1
            return self.__list.insert(index, module)
        else:
            raise Exception("Submodule list: Module is already loaded of given id")

    def clear(self):
        self.__size = 0
        self.__list.clear()
        self.__list = [-1] * self.__predefined_max

    # Getter for modules
    def get_by_id(self, id):
        return self.__list[self.__map_id_to_index(id)]
