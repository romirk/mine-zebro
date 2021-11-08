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
    __listen_for_commands_interval = 3  # used by thread to sleep after seeing no command was given (in seconds)
    __listen_for_module_output_interval = 1
    __wait_for_module_to_join = 5
    is_command_loaded = False
    __mcp_command = ""
    __server_id = ""

    # Public Variables & Flags
    output = ""  # output data from modules read by MCP from here
    is_output_loaded = False
    is_shut_down = False
    halt_module_execution = False

    def __init__(self):
        self.lock = threading.Lock()

    # initialisation before entering listening loop
    def start(self):
        self.__send_text_to_user("Router has started")
        self.is_shut_down = False
        self.__listen_to_commands()

    # loop until command given by mcp (if no command sleep to an appropriate amount of time)
    def __listen_to_commands(self):
        while not self.is_shut_down:
            # If no command to execute sleep
            if not self.is_command_loaded:
                time.sleep(self.__listen_for_commands_interval)
            else:
                # else execute
                output = Array('i', 100)
                is_output_loaded = Value('i', 0)
                halt_process = Value('i', 0)
                module_thread: Process = Process(target=execute,
                                                 args=(self.__server_id,
                                                       self.__mcp_command,
                                                       output,
                                                       is_output_loaded,
                                                       halt_process,))
                module_thread.name = "module_thread"
                module_thread.daemon = True

                self.__prepare()

                module_thread.start()  # start module process
                while module_thread.is_alive():
                    if is_output_loaded.value == 1:
                        self.__send_array_to_user(output)
                        is_output_loaded.value = 0

                    elif self.halt_module_execution:
                        halt_process.value = 1
                        module_thread.join(self.__wait_for_module_to_join)

                    else:
                        time.sleep(self.__listen_for_module_output_interval)

                # check after process finished if anything loaded while sleeping
                if is_output_loaded.value == 1:
                    self.__send_array_to_user(output)
                    is_output_loaded.value = 0

                self.__clean_up()
        return

    # Note: All functions that change attributes need to use lock to avoid deadlock
    # called before each command is executed
    def __prepare(self):
        self.lock.acquire()
        self.output = ""
        self.is_output_loaded = False
        self.halt_module_execution = False
        self.lock.release()

    # called after each command is executed
    def __clean_up(self):
        self.lock.acquire()
        self.is_command_loaded = False
        self.__mcp_command = ""
        self.__server_id = ""
        self.lock.release()

    # return a text output to the user
    def __send_text_to_user(self, text):
        while self.is_output_loaded:
            time.sleep(1)
        self.lock.acquire()
        self.is_output_loaded = True
        self.output = text
        self.lock.release()

    # transform a array of characters into a string and send to user
    def __send_array_to_user(self, output: SynchronizedString):
        output.acquire()
        text = array_to_string(output)
        output.release()
        self.__send_text_to_user(text)

    # called by mcp to load a command to be executed
    def load_command(self, command, id):
        self.lock.acquire()
        self.__mcp_command = command
        self.__server_id = id
        self.is_command_loaded = True
        self.lock.release()


#process created by the router runs here
def execute(destination, command, output_array, is_output_loaded, halt_process):
    print("Process started")
    server_module = __get_module(destination, output_array, is_output_loaded, halt_process)
    if server_module == "":
        string_to_array("No such module", output_array)
        is_output_loaded.value = True
        return
    else:
        server_module.execute(command)
        return


#transforms a string into an array
def string_to_array(string, array):
    for i in range(min(len(array), len(string))):
        array[i] = ord(string[i])


#transforms an array into a string
def array_to_string(array):
    result = ""
    for i in range(len(array)):
        #avoid null characters
        if 126 >= array[i] >= 32:
            result += chr(array[i])
    return result


#retrive module #TODO add all modules here
def __get_module(destination, output_array, is_output_loaded, halt_process):
    if destination == "dummy":
        return dummyModule.DummyManager(output_array, is_output_loaded, halt_process)

    elif destination == "loco":
        return

    elif destination == "com":
        return
    else:
        return ""
