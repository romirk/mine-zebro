from abc import ABC, abstractmethod

# Abstract class that all modules inherit from
# See dummyModule.py for how example
from enum import Enum


class Module(ABC):

    @abstractmethod
    def __init__(self, router):
        if not isinstance(router, router.__class__):
            raise Exception("Module:" + self.get_id() + " input parameter not a router")
        self.__router = router
        pass

    @abstractmethod
    def setup(self):
        pass

    # The following 3 methods first call super and add functionality
    # id must not include any digits
    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def help(self):
        text = str(self.get_id()) + " module commands\n"
        return text
        pass

    # main function of module (note use super().execute before doing anything else)
    @abstractmethod
    def execute(self, command):
        pass

    @abstractmethod
    # method delivers data to mcp use super().send_to_mcp to execute
    def send_to_router(self, code: int, msg=None, data=None):
        self.__router.send_package_to_mcp(create_router_package(code, msg, data), False)
        pass

    @abstractmethod
    # method that check if module should stop execution
    def check_if_halt(self):
        temp = self.__router.halt_module_execution
        return temp
        pass

    @abstractmethod
    def command_does_not_exist(self, command):
        text = self.get_id() + ": " + "no such command"
        self.send_to_router(OutputCode.error.value, text)
        pass


class OutputCode(Enum):
    data = 0
    error = 1
    warning = 2


# Function called by all modules to deliver information to the router
def create_router_package(code: int, msg=None, data=None):
    return {'code': code, 'message': msg, 'data': data}
