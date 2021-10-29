import commsApi
import threading

class MessageManager:

    command_received = False
    __command = ""

    #Wrap this class around a comms module
    def __init__(self, comms):
        if not isinstance(comms, commsApi.AbstractComms.__class__):
            self.__comms = comms
        else:
            raise Exception("MessageManager: constructor object not of type commsApi")

    #MCP to Cooms methods
    #starts communication module
    def start(self):
        listen_to_user_thread = threading.Thread(target=self.listen_to_user(), args=())
        listen_to_user_thread.start()
        self.__comms.start()

    #Comms to MCP methods
    def listen_to_user(self):
        while True:
            self.__command = self.__comms.get_command_from_user()
            command_received = True

    def get_destination(self, data):
        return data.split(" ", 1).__getitem__(0)

    def get_command(self, data):
        return data.split(" ", 1).__getitem__(1)

    #MCP to Comms
    def send_to_user(self, output, time, error, process_completed):
        #Edit data to make it presentable
        self.__comms.send_response_to_user(output)