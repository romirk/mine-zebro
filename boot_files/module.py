from abc import ABC, abstractmethod
import router


# Abstract class that all modules inherit from
class Module(ABC):
    @abstractmethod
    def get_id(self):
        pass

    #main function of module (note use super().execute before doing anything else)
    @abstractmethod
    def execute(self, command, router):
        if not isinstance(router,router.__class__):
            raise Exception("Module:" + self.get_id()+ " input parameter not a router")
        pass

    @abstractmethod
    #method delivers data to mcp use super().send_to_mcp to execute
    def send_to_mcp(self, router, data, error):
        router.send_data_to_mcp(data,error)
        pass
