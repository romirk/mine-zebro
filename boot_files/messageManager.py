import time

import threading


# Wrapper for comms that transfers messages between comms and mcp
class MessageManager:
    is_shut_down = False
    __sleep_interval = 1
    # variables shared that need locks to write on are:
    __stored_input = ""
    input_received = False

    def __init__(self, comms):
        self.__comms = comms
        self.__comms.setup()
        self.__lock = threading.Lock()

    # Comms to MCP methods
    # loop for waiting for user input
    def listen_to_user(self):
        while not self.is_shut_down:
            command = self.__get_valid_input()
            self.__set_command(command)
            time.sleep(self.__sleep_interval)

    # Get valid input from comms
    def __get_valid_input(self):
        user_input = self.__comms.cin()  # blocking method

        if len(user_input.split(" ", 1)) < 2:
            user_input = "mcp " + user_input

        return user_input.lower()

    # store given command as object attribute
    def __set_command(self, command):
        self.__lock.acquire()
        self.__stored_input = command
        self.input_received = True
        self.__lock.release()

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

    def reset_input_received(self):
        self.__lock.acquire()
        self.input_received = False
        self.__lock.release()

    # MCP to Comms
    def send_to_user_package(self, output, time, error, process_completed):
        # Edit data to make it presentable
        text = output + " Time:" + str(time) + " Error:" + str(error) + "  Completed:" + str(process_completed)
        self.send_to_user_text(text)

#CameraManager packages use as command_id = frame #id
    def send_to_user_package2(self, package: dict):
        # Edit data to make it presentable
        self.send_to_user_text(package)

    def send_to_user_text(self, text):
        self.__lock.acquire()
        self.__comms.cout(text)
        self.__lock.release()

    # loop that periodically sets command to check battery status and if motors are overheating
    # note if status sleep interval is 0 then disabled
    def status_loop(self, sleep_interval):
        battery_level = 100
        while not self.is_shut_down and sleep_interval > 0:
            # TODO check for battery status & implement as module or mcp command depending if it's using I2C bus
            battery_level -= 5
            if 20 > battery_level:
                self.__set_command("dummy count")
            # TODO add check for overheating
            time.sleep(sleep_interval)

        return


#Function called by all threads that need to deliver information to the user
def create_package(command_id: str, output, timestamp, is_process_complete=None):
    return {'command_id': command_id, 'output': output, 'timestamp': timestamp, 'is_process_complete': is_process_complete}
