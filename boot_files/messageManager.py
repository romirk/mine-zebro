import time
import json
import commsApi
from typing import Union

import module
from datetime import datetime

import commsApi

import threading


# Wrapper for comms that transfers messages between comms and mcp
class MessageManager:
    is_shut_down = False
    __status_counter_max = 60  # how often to check motors for overheating or battery in seconds (set to 0 so not to check)
    __sleep_interval = 1
    __status_sleep_interval = 3
    # variables shared that need locks to write on are:
    __stored_input = ""
    input_received = False

    def __init__(self, comms: commsApi.AbstractComms, is_pc: bool, event: threading.Event.__class__) -> None:
        self.__comms = comms
        self.__comms.setup()
        self.__lock = threading.Lock()
        self.__isPc = is_pc
        self.__event = event

    # Comms to MCP methods
    # loop for waiting for user input
    def listen_to_user(self) -> None:
        while not self.is_shut_down:
            time.sleep(1)  # needed since it blocks processes from starting
            command = self.__get_valid_input()
            self.__set_command(command)

    # Get valid input from comms
    def __get_valid_input(self) -> str:
        user_input = self.__comms.cin()  # blocking method

        while user_input == "":
            user_input = self.__comms.cin()
            time.sleep(self.__sleep_interval)

        if len(user_input.split(" ", 1)) < 2:
            user_input = "mcp " + user_input

        return user_input.lower()

    # store given command as object attribute
    def __set_command(self, command: str) -> None:
        self.__lock.acquire()
        self.__stored_input = command
        self.input_received = True
        self.__lock.release()
        self.__event.set()

    #public methods used by MCP

    def get_destination(self) -> str:
        self.__lock.acquire()
        destination = self.__stored_input.split(" ", 1).__getitem__(0)
        self.__lock.release()
        return destination

    def get_command(self) -> str:
        self.__lock.acquire()
        command = self.__stored_input.split(" ", 1).__getitem__(1)
        self.__lock.release()
        return command

    def reset_input_received(self) -> None:
        self.__lock.acquire()
        self.input_received = False
        self.__lock.release()

    # CameraManager packages use as command_id = frame #id
    def send_to_user_package(self, package: dict) -> None:
        self.__lock.acquire()
        # array is not json serializable hence turn into python list
        temp = json.dumps(package, indent=1)
        self.__comms.cout(temp)
        self.__lock.release()

    # loop that periodically sets command to check battery status and if motors are overheating
    # note if status sleep interval is 0 then disabled
    # disabled battery check
    def status_loop(self) -> None:
        counter = self.__status_counter_max  # when counter > status_sleep_interval send one of commands
        number = 0  # used to choose which of the two checks to do
        while not self.is_shut_down and self.__status_counter_max > 0:
            # TODO check for battery status & implement as module or mcp command depending if it's using I2C bus
            # TODO add check for overheating
            # wait for user to stop sending data
            while self.input_received:
                time.sleep(self.__sleep_interval)

            if counter >= self.__status_counter_max:
                if number % 2 != 0 and counter:  # check if odd
                    if self.__isPc:
                        self.__set_command("dummy battery")
                    else:
                        self.__set_command("loc get m:all temperature")
                else:
                    if self.__isPc:
                        self.__set_command("dummy battery")
                number += 1
                counter = 0

            counter += self.__status_sleep_interval  # counter increase by waiting time
            time.sleep(self.__status_sleep_interval)

        return


# Function called by all threads that need to deliver information to the user
def create_user_package(command_id: str, timestamp: str, output: Union[dict, str, list] = None,
                        has_process_completed: bool = None) -> dict:
    return {'command_id': command_id, 'package': output, 'timestamp': timestamp,
            'has_process_completed': has_process_completed}


#
# def mcp_user_package(command_id: str, code: int, message: str, has_process_completed: bool = None) -> dict:
#    output = module.create_router_package(code, message)
#    return create_user_package(command_id, datetime.now().strftime("%H:%M:%S"), output, has_process_completed)


# comms Implementation using the terminal as input/package
class CommsMock(commsApi.AbstractComms):

    def setup(self) -> None:
        return

    def cin(self) -> str:
        return input("rinzler>")

    def cout(self, output: str) -> None:
        print("output>" + output)
