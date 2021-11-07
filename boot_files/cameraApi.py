from abc import ABC, abstractmethod


#Module that captures frames to be forwarded to the user
class AbstractCamera(ABC):

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def frame_capture(self):
        pass

    @abstractmethod
    def get_frame(self):
        pass

    @abstractmethod
    def exit(self):
        pass