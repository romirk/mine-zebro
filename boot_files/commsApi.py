from abc import ABC, abstractmethod


#Module responsible for communication with user
class AbstractComms(ABC):

    @abstractmethod
    def setup(self) -> None:
        pass

    @abstractmethod
    def cin(self) -> str:
        pass

    @abstractmethod
    def cout(self, package: dict) -> None:
        pass
