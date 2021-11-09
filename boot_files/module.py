from abc import ABC, abstractmethod


# Abstract class that all modules inherit from
# See dummyModule.py for how example
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

    #The following 3 methods first call super and add functionality
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
    #method delivers data to mcp use super().send_to_mcp to execute
    def send_to_mcp(self, data, error):
        self.__router.send_data_to_mcp(data, error)
        pass

    @abstractmethod
    #method that check if module should stop execution
    def check_if_halt(self):
        temp = self.__router.halt_module_execution
        return temp
        pass

    @abstractmethod
    def command_does_not_exist(self, command):
        text = self.get_id() + ": " + "no such command"
        self.send_to_mcp(text, -1)
        pass


