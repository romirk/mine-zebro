import time

import commsApi
import threading


class MessageManager:
    command_received = False
    __command = ""
    is_shut_down = False
    __sleep_interval = 1

    # Wrap this class around a comms module
    def __init__(self, comms):
        if not isinstance(comms, commsApi.AbstractComms.__class__):
            self.__comms = comms
            self.__comms.setup()
        else:
            raise Exception("MessageManager: constructor object not of type commsApi")

    # Comms to MCP methods
    # loop for waiting for user input
    def listen_to_user(self, lock):
        while not self.is_shut_down:
            temp = self.__comms.get_user_input()  # blocking method
            lock.acquire()
            self.__command = temp
            # Check if command is valid
            if len(self.__command.split(" ", 1)) < 2:
                raise Exception("messenger: command invalid add space")
            self.command_received = True
            lock.release()
            time.sleep(self.__sleep_interval)

    def get_destination(self):
        return self.__command.split(" ", 1).__getitem__(0)

    def get_command(self):
        return self.__command.split(" ", 1).__getitem__(1)

    # MCP to Comms
    def router_send_to_user(self, output, time, error, process_completed):
        # Edit data to make it presentable
        self.__comms.send_response(output)

    def mcp_send_to_user(self, output, time):
        self.__comms.send_response(output)
