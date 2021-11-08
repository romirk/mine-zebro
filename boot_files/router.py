import ctypes
import multiprocessing
from multiprocessing import Process, Manager, Value, Array
import threading
from multiprocessing.sharedctypes import SynchronizedString

import dummyModule
import module
import time
from datetime import datetime


# responsible for sending/ receiving messages between MCP and the submodules
# only one module can communicate with the MCP throughout the bus at a time thus only one connection used
# Establishes connection between module(server) and MCP
class Router:
    # Private Variables only accessed by Router
    __sleep_interval = 3  # used by thread to sleep after seeing no command was given (in seconds)
    __is_command_loaded = False
    __mcp_command = ""
    __server_id = ""

    # Public Variables & Flags
    output = ""  # output data from modules read by MCP from here
    is_output_loaded = False
    is_shut_down = False
    hold_module_execution = False

    def __init__(self):
        self.lock = threading.Lock()
        self.__process_lock = multiprocessing.Lock()

    # initialisation before entering listening loop
    def start(self):
        self.send_text_to_user("Router has started")
        self.is_shut_down = False
        self.__listen_to_commands()

    # loop until command given by mcp (if no command sleep to an appropriate amount of time)
    def __listen_to_commands(self):
        while not self.is_shut_down:
            # If no command to execute sleep
            if not self.__is_command_loaded:
                time.sleep(self.__sleep_interval)
            else:
                # else execute
                output = Array('i', 100)
                is_output_loaded = Value(ctypes.c_bool, False)
                hold_process = Value(ctypes.c_bool, False)
                module_thread: Process = Process(target=execute,
                                                 args=(self.__server_id,
                                                       self.__mcp_command,
                                                       output,
                                                       is_output_loaded,
                                                       hold_process,
                                                       self.__process_lock,))
                module_thread.name = "module_thread"
                module_thread.daemon = True

                self.__prepare()

                module_thread.run()  # start module process
                while module_thread.is_alive():
                    if is_output_loaded.value:
                        self.send_array_to_user(output)
                        is_output_loaded.value = False
                    else:
                        time.sleep(self.__sleep_interval)

                # check after process finished if anything loaded while sleeping
                if is_output_loaded.value:
                    self.send_array_to_user(output)
                    is_output_loaded.value = False

                self.__clean_up()
        return

    # Note: All functions that change attributes need to use lock to avoid deadlock
    # called before each command is executed
    def __prepare(self):
        self.lock.acquire()
        self.output = ""
        self.is_output_loaded = False
        self.hold_module_execution = False
        self.lock.release()

    # called after each command is executed
    def __clean_up(self):
        self.lock.acquire()
        self.__is_command_loaded = False
        self.__mcp_command = ""
        self.__server_id = ""
        self.lock.release()

    # called by active module to return data to mcp
    def send_text_to_user(self, output):
        while self.is_output_loaded:
            time.sleep(1)
        self.lock.acquire()
        self.is_output_loaded = True
        self.output = output
        self.lock.release()

    # called by active module to return data to mcp
    def send_array_to_user(self, output: SynchronizedString):
        output.acquire()
        text = array_to_string(output)
        output.release()
        self.send_text_to_user(text)

    # called by mcp to load a command to be executed
    def load_command(self, command, id):
        self.lock.acquire()
        self.__mcp_command = command
        self.__server_id = id
        self.__is_command_loaded = True
        self.lock.release()


def execute(destination, command, output_array, is_output_loaded, hold_process, process_lock):
    print("Process started")
    server_module = get_module(destination, output_array)
    if server_module == "":
        string_to_array("No such module", output_array)
        is_output_loaded.value = True
        return
    else:
        server_module.execute(command)
        return


#transforms a string into an array
def string_to_array(string, output_array):
    for i in range(min(len(output_array), len(string))):
        output_array[i] = ord(string[i])


#transforms an array into a string
def array_to_string(output_array):
    result = ""
    for i in range(len(output_array)):
        if 126 >= output_array[i] >= 32:
            result += chr(output_array[i])
    return result


def get_module(destination, output_array):
    if destination == "dummy":
        return dummyModule.DummyManager(output_array)

    elif destination == "loco":
        return

    elif destination == "com":
        return
    else:
        return ""
