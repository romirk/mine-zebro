from abc import ABC, abstractmethod


# Abstract class that all modules inherit from
# See dummyModule.py for how example
class Module(ABC):

    @abstractmethod
    def __init__(self, output_array):
        self.output_array = output_array

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
    def send_to_mcp(self, output):
        self.output_array = list(output[:len(self.output_array)])
        pass

    @abstractmethod
    #method that check if module should stop execution
    def check_if_hold(self):
        #temp = self.__router.hold_module_execution
        return False
        pass

    @abstractmethod
    def command_does_not_exist(self, command):
        text = self.get_id() + ": " + "no such command"
        self.send_to_mcp(text)
        pass


