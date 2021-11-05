from abc import ABC, abstractmethod
import module


#Module responsible for communication with user
class AbstractComms(ABC):

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def cin(self):
        pass

    @abstractmethod
    def cout(self, string):
        pass
