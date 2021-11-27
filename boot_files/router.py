import threading
from enum import Enum
from multiprocessing.managers import DictProxy
from typing import List, Union

import dummyModule
import messageManager
import module
import time

try:  # prevent errors when testing on computer
    from smbus2 import SMBus
except:
    SMBus = int

from datetime import datetime


# responsible for sending/ receiving messages between MCP and the submodules
# only one module can communicate with the MCP throughout the bus at a time thus only one connection used
# Establishes connection between module(server) and MCP
class Router:
    __sleep_interval = 3  # used by thread to sleep after seeing no command was given (in seconds)

    def __init__(self, shared_data) -> None:
        self.__list = Submodules()  # list of submodules
        self.lock = shared_data[Str.lock.value]
        self.__bus = SMBus(1)  # create bus
        self.shared_data = shared_data

    # initialisation before entering listening loop
    def start(self) -> None:
        self.__clean_up()
        self.__prepare()
        self.shared_data[Str.is_shut_down.value] = False
        self.__setup_all_modules()
        self.listen_to_commands()

    # Given a module by MCP add to submodules list
    def __add_module(self, new_module: module.Module) -> None:
        self.__list.add_by_id(new_module.get_id(), new_module)

    # Use this method to add all modules to the current router instance
    def __setup_all_modules(self) -> None:
        # TODO start all other modules here
        self.__add_module(dummyModule.DummyManager(self, self.__bus))

        self.__list.setup()  # calls setup method in each module
        return

    # loop until command given by mcp (if no command sleep to an appropriate amount of time)
    def listen_to_commands(self) -> None:
        while not self.shared_data[Str.is_shut_down.value]:
            # If no command to execute sleep
            if not self.shared_data[Str.is_command_loaded.value]:
                time.sleep(self.__sleep_interval)
            else:
                # else execute
                server_id = "".join(
                    [i for i in self.shared_data[Str.prefix.value] if
                     not i.isdigit()])  # remove identifier which is a number
                if not self.__list.check_id(server_id):
                    self.send_package_to_mcp(module.create_router_package(module.OutputCode.error.value,
                                                                          "Failed to fetch module: " + str(server_id)),
                                             False)
                    self.__clean_up()
                else:
                    server = self.__list.get_by_id(server_id)
                    self.__prepare()
                    server.execute(self.shared_data[Str.command.value])  # blocking method
                    self.send_package_to_mcp(module.create_router_package(module.OutputCode.data.value,
                                                                          "Completed"),
                                             True)
                    self.__clean_up()

    # Note: All functions that change attributes need to use routerLock to avoid deadlock
    # called before each command is executed
    def __prepare(self) -> None:
        self.lock.acquire()
        self.shared_data[Str.is_halt.value] = False
        self.lock.release()

    # called after each command is executed
    def __clean_up(self) -> None:
        self.lock.acquire()
        self.shared_data[Str.is_command_loaded.value] = False
        self.shared_data[Str.command.value] = ""
        self.shared_data[Str.prefix.value] = ""
        self.lock.release()

    # called by active module to return data to mcp
    def send_package_to_mcp(self, module_output: dict, has_process_completed: bool) -> None:
        while self.shared_data[Str.is_package_ready.value]:
            time.sleep(1)
        self.lock.acquire()

        # in case of automated call to check battery or motors place the appropriate prefix
        if self.shared_data[Str.command.value] == "battery":
            self.shared_data[Str.prefix.value] = "battery"
        elif self.shared_data[Str.command.value] == "motors":
            self.shared_data[Str.prefix.value] = "motors"

        self.shared_data[Str.package.value] = messageManager.create_user_package(
            self.shared_data[Str.prefix.value],
            datetime.now().strftime("%H:%M:%S"),
            module_output,
            has_process_completed)
        self.shared_data[Str.is_package_ready.value] = True
        self.lock.release()

    # Use this method to remove all modules from the list
    def clear_modules_list(self) -> None:
        self.__list.clear()
        return


# list of submodules contained in the router
class Submodules:
    __id_list = ["com", "loco", "dummy"]  # every module needs to implement a getter for their id
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


# Class shows all internal states mcp can be active in
class Str(Enum):
    lock = "routerLock"
    is_shut_down = "is_shut_down"
    is_halt = "is_halt"
    is_command_loaded = "is_command_loaded"
    is_package_ready = "is_package_ready"
    prefix = "prefix"
    command = "command"
    package = "package"


def start(shared_data: DictProxy):
    router = Router(shared_data)
    print("Router Process has started")

    router.start()
    return
