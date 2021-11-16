from abc import ABC, abstractmethod
import router
try: #prevent errors when testing on computer
    from smbus2 import SMBus
except: SMBus = int

# Abstract class that all modules inherit from
# See dummyModule.py for how example
from enum import Enum


class Module(ABC):

    @abstractmethod
    def __init__(self, router_obj, bus: SMBus = None) -> None:
        self.__router = router_obj
        self.__bus = bus

    @abstractmethod
    def setup(self) -> None:
        pass

    # The following 3 methods first call super and add functionality
    # id must not include any digits
    @abstractmethod
    def get_id(self) -> str:
        pass

    def get_status(self):
        pass

    @abstractmethod
    def help(self) -> str:
        text = str(self.get_id()) + " module commands\n"
        return text

    # main function of module (note use super().execute before doing anything else)
    @abstractmethod
    def execute(self, command: str) -> None:
        pass

    # method delivers data to mcp use super().send_to_mcp to execute
    def send_to_router(self, code: int, msg: str = None, data=None) -> None:
        self.__router.send_package_to_mcp(create_router_package(code, msg, data), False)

    def send_output(self, packet=None, code=None, msg=None, data=None):
        if not packet:
            packet = dict(code=code, msg=msg, data=data)
        self.send_to_router(**packet)

    # method that check if module should stop execution
    def check_halt_flag(self) -> bool:
        temp = self.__router.shared_data[router.Str.is_halt.value]
        return temp

    def command_does_not_exist(self, command: str) -> None:
        text = self.get_id() + ": " + "no such command"
        self.send_to_router(OutputCode.error.value, text)


class OutputCode(Enum):
    data = 0
    error = 1
    warning = 2


# Function called by all modules to deliver information to the router
def create_router_package(code: int, msg: str = None, data=None):
    return {'code': code, 'msg': msg, 'data': data}
