import commsApi
import threading

class MessageManager:

    #TODO access to this variables should be synchronous since used by 2 threads
    #https://www.youtube.com/watch?v=rQTJuCCCLVo
    command_received = False
    __command = ""

    #Wrap this class around a comms module
    def __init__(self, comms):
        if not isinstance(comms, commsApi.AbstractComms.__class__):
            self.__comms = comms
            self.__comms.setup()
        else:
            raise Exception("MessageManager: constructor object not of type commsApi")

#Comms to MCP methods
    #loop for waiting for user input
    def listen_to_user(self, lock):
        while True:
            temp = self.__comms.get_user_input() #blocking method
            self.__command = temp
            command_received = True

    def get_destination(self, data):
        return data.split(" ", 1).__getitem__(0)

    def get_command(self, data):
        return data.split(" ", 1).__getitem__(1)

    #MCP to Comms
    def send_to_user(self, output, time, error, process_completed):
        #Edit data to make it presentable
        self.__comms.send_response(output)