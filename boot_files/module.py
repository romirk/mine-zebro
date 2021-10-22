from abc import ABC, abstractmethod


class Module(ABC):
    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def execute(self, command):
        pass
