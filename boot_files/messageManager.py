import time

import commsApi
import threading


class MessageManager:
    is_shut_down = False
    __sleep_interval = 1
    #variables shared between threads that need locks to write on are:
    __stored_input = ""
    input_received = False

    # Wrap this class around a comms module
    #TODO Fix bug here when checking for comms
    def __init__(self, comms, lock):
        if not isinstance(comms, commsApi.AbstractComms.__class__):
            self.__comms = comms
            self.__comms.setup()
            self.__lock = lock
        else:
            raise Exception("MessageManager: constructor object not of type commsApi")

    # Comms to MCP methods
    # loop for waiting for user input
    def listen_to_user(self):
        while not self.is_shut_down:
            command = self.__get_valid_input()
            self.__set_command(command)
            time.sleep(self.__sleep_interval)

    #Get valid input from the comms
    def __get_valid_input(self):
        user_input = self.__comms.cin()  # blocking method
        # check if input has at least two parts source/destination to be considered valid
        # if not repeat
        while len(user_input.split(" ", 1)) < 2:
            self.send_to_user_text("messenger: command invalid add space")
            user_input = self.__comms.cin()

        return user_input.lower()

    #store given command as object attribute
    def __set_command(self, command):
        self.__lock.acquire()
        self.__stored_input = command
        self.input_received = True
        self.__lock.release()

    def get_destination(self):
        self.__lock.acquire()
        destination = self.__stored_input.split(" ", 1).__getitem__(0)
        self.__lock.release()
        return destination

    def get_command(self):
        self.__lock.acquire()
        command = self.__stored_input.split(" ", 1).__getitem__(1)
        self.__lock.release()
        return command

    def reset_input_received(self):
        self.__lock.acquire()
        self.input_received = False
        self.__lock.release()

    # MCP to Comms
    def send_to_user_package(self, output, time, error, process_completed):
        # Edit data to make it presentable
        text = output + " Time:" + str(time) + " Error:" + str(error) + "  Completed:" + str(process_completed)
        self.send_to_user_text(text)

    def send_to_user_text(self, text):
        self.__lock.acquire()
        self.__comms.cout(text)
        self.__lock.release()
