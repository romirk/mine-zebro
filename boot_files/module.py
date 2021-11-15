from abc import ABC, abstractmethod
import router
try: #prevent errors when testing on computer
    from smbus2 import SMBus
except: SMBus = int

# Abstract class that all modules inherit from
# See dummyModule.py for how example
from enum import Enum



class OutputCode(Enum):
    data = 0
    error = 1
    warning = 2


class Module(ABC):

    ### INITIALISATION

    @abstractmethod
    def __init__(self, router_obj, bus: SMBus = None) -> None:
        self.__router = router_obj
        self.__bus = bus


    ### ABOUT
        
    # id must not include any digits
    @abstractmethod
    def get_id(self) -> str:
        pass

    @abstractmethod
    def help(self) -> str:
        text = str(self.get_id()) + " module commands\n"
        return text




    ### I2C INSTRUCTIONS

    # run whatever needs to be done to set up the system
    @abstractmethod
    def setup(self) -> None:
        pass

    #get system status. behaves like execute
    def get_status(self):
        pass

    # main function of module (note use super().execute before doing anything else)
    @abstractmethod
    def execute(self, command: str) -> None:
        pass



    ### HALTING EXECUTION

    # method that check if module should stop execution
    def check_halt_flag(self) -> bool:
        temp = self.__router.halt_module_execution
        return temp



    ### OUTPUT
    
    # method delivers data to mcp
    def send_output(self, packet=None, code=0, msg=None, data=None):
        if not packet:
            packet = create_router_package(code=code, msg=msg, data=data)
        self.__router.send_package_to_mcp(package, False)


    #functions for creating packages
    def _halt(self):
        return self._error("Execution halted")
    def _invalid_command(self,err=""):
        if err:
            return self._error("Invalid command: %s"%err)
        return self._error("Invalid command")
    
    def _error(self,err,data={}):
        if data:
            return create_router_package(code=OutputCode.error.value,msg=err,data=data)
        else:
            return create_router_package(code=OutputCode.error.value,msg=err)
    def _warning(self,err,data={}):
        if data:
            return create_router_package(code=OutputCode.warning.value,msg=err,data=data)
        else:
            return create_router_package(code=OutputCode.warning.value,msg=err)
    def _info(self,msg):
        return create_router_package(code=OutputCode.data.value,msg=msg)
    def _data(self,data,msg="Sent data"):
        return create_router_package(code=OutputCode.data.value,msg=msg,data=data)






# Function called by all modules to deliver information to the router
def create_router_package(code: int = OutputCode.data.value, msg: str = "", data={}):
    return dict(code=code, msg=msg, data=data)
