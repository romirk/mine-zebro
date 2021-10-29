from abc import ABC, abstractmethod
import module


#Module responsible for communication with user
class AbstractComms(ABC):

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def get_user_input(self):
        pass

    @abstractmethod
    def send_response(self, response):
        pass
