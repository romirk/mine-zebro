import threading
from enum import Enum
from typing import List, Union

import dummyModule
import messageManager
import module
import time

from datetime import datetime

import os, sys

# MODULE IMPORTS
try:  # prevent errors when testing on computer
    from smbus2 import SMBus

    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "locomotion"))
    import LocomotionApp

    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lidar"))
    import LIDARApp

    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "environmental"))
    import EnvironmentalApp

    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bms"))
    import BMSApp
except:
    SMBus = int


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

    def __init__(self, isPc: bool, lock: threading.Lock.__class__, event: threading.Event.__class__) -> None:
        self.__list = Submodules()  # list of submodules
        self.lock = lock
        self.__bus = SMBus(1)  # create bus
        self.isPc = isPc
        self.mcp_event = event

    # initialisation before entering listening loop
    def start(self) -> None:
        self.__clean_up()
        self.__prepare()
        self.is_shut_down = False
        self.__setup_all_modules()
        self.__listen_to_commands()

    # Given a module by MCP add to submodules list
    def __add_module(self, new_module: module.Module) -> None:
        self.__list.add_by_id(new_module.get_id(), new_module)

    # Use this method to add all modules to the current router instance
    def __setup_all_modules(self) -> None:
        # TODO start all other modules here
        if self.isPc:
            self.__add_module(dummyModule.DummyManager(self, self.__bus))
        else:
            for module_class in [dummyModule.DummyManager, BMSApp.BMSApp, LocomotionApp.LocomotionApp,
                                 LIDARApp.LIDARApp, EnvironmentalApp.EnvironmentalApp]:
                self.__add_module(module_class(self, self.__bus))

        self.__list.setup()  # calls setup method in each module
        return

    # loop until command given by mcp (if no command sleep to an appropriate amount of time)
    def __listen_to_commands(self) -> None:
        while not self.is_shut_down:
            # If no command to execute sleep
            if not self.is_command_loaded:
                time.sleep(self.__sleep_interval)
            else:
                # else execute
                server_id = "".join(
                    [i for i in self.__prefix if not i.isdigit()])  # remove identifier which is a number
                if not self.__list.check_id(server_id):
                    self.send_package_to_mcp(module.create_router_package(module.OutputCode.error.value,
                                                                          "Failed to fetch module: " + str(server_id)),
                                             False)
                    self.__clean_up()
                else:
                    server = self.__list.get_by_id(server_id)
                    self.__prepare()
                    server.execute(self.__command)  # blocking method
                    self.send_package_to_mcp(module.create_router_package(module.OutputCode.data.value,
                                                                          "Completed"),
                                             True)
                    self.__clean_up()

    # Note: All functions that change attributes need to use lock to avoid deadlock
    # called before each command is executed
    def __prepare(self) -> None:
        self.lock.acquire()
        self.package = ""
        self.halt_module_execution = False
        self.lock.release()

    # called after each command is executed
    def __clean_up(self) -> None:
        self.lock.acquire()
        self.is_command_loaded = False
        self.__command = ""
        self.__prefix = ""
        self.lock.release()

    # called by active module to return data to mcp
    def send_package_to_mcp(self, module_output: dict, has_process_completed: bool) -> None:
        while self.is_package_loaded:
            time.sleep(1)
        self.lock.acquire()

        # in case of automated call to check battery or motors place the appropriate prefix
        if self.__command == "battery":
            self.__prefix = "battery"
        elif self.__command == "motors":
            self.__prefix = "motors"

        self.package = messageManager.create_user_package(self.__prefix,
                                                          datetime.now().strftime("%H:%M:%S"),
                                                          module_output,
                                                          has_process_completed)
        self.is_package_loaded = True
        self.lock.release()
        self.mcp_event.set()

    # called by mcp to load a command to be executed
    def load_command(self, prefix: str, command: str) -> None:
        self.lock.acquire()
        self.__command = command
        self.__prefix = prefix
        self.is_command_loaded = True
        self.lock.release()

    # Use this method to remove all modules from the list
    def clear_modules_list(self) -> None:
        self.__list.clear()
        return


# list of submodules contained in the router
class Submodules:
    __id_list = ["com", "bms", "loc", "lidar", "env", "dummy"]  # every module needs to implement a getter for their id
    __predefined_max = len(__id_list)  # should be equal to the max number of modules
    __size = 0

    # List of submodules that is stored by the router
    def __init__(self) -> None:
        self.__list = [-1] * self.__predefined_max

    def setup(self) -> None:
        for i in range(self.__predefined_max):
            obj = self.__list.__getitem__(i)
            if isinstance(obj, module.Module.__class__):
                obj.setup()

    def check_id(self, identifier: str) -> bool:
        return self.__id_list.__contains__(identifier)

    def is_in_list(self, submodule: module.Module) -> bool:
        return self.__list.__contains__(submodule)

    # Used for adding modules
    def __map_id_to_index(self, identifier: str) -> int:
        if self.check_id(identifier):
            return self.__id_list.index(identifier)
        raise Exception("Submodule list: id <" + identifier + "> does not exist")

    def add_by_id(self, identifier: str, new_module: module.Module):
        index = self.__map_id_to_index(identifier)
        if not self.is_in_list(new_module):
            self.__size += 1
            return self.__list.insert(index, new_module)
        else:
            raise Exception("Submodule list: Module is already loaded of given id")

    def clear(self) -> None:
        self.__size = 0
        self.__list.clear()
        self.__list = [-1] * self.__predefined_max

    # Getter for modules
    def get_by_id(self, identifier: str) -> Union[module.Module, int]:
        return self.__list[self.__map_id_to_index(identifier)]
