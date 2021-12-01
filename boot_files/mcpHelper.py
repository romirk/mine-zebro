import threading
import time
from datetime import datetime

import messageManager
import router
import rinzler

try:
    from leds import LEDs
except:
    LEDs = int


# Class holds mcp functionality relating to handling commands, setting up threads
# Note all methods that receive parameters from commands check if they are valid and if not send respond back to the user


class McpHelper:
    _command_not_found_string = "MCP command does not exist"

    def __init__(self, mcp) -> None:
        self.mcp = mcp
        # setting up some important multithreading objects
        self.mcp.event = threading.Event()
        self.leds = LEDs()

        # checks to see if the program is run on the rover and not a linux pc
        if not isinstance(self.leds, int):
            self.leds.start()  # turns on pwm, but at 0 power
            self.mcp.is_host_pc = False

    def handle_command(self, prefix: str, command: str) -> None:
        data = ""
        has_process_completed = True
        if command == "terminate":
            self.mcp.internal_state = rinzler.State.Terminate.value

        elif command == "shutdown":
            self.__shutdown_procedure()
            self.mcp.internal_state = rinzler.State.ShutDown.value
            
        elif command.startswith("lights"):
            data = self.__lights(command)

        elif command == "help":
            data = self.__help()

        elif command == "restart":
            self.__shutdown_procedure()
            self.mcp.internal_state = rinzler.State.Restart.value

        elif command == "reset":
            self.mcp.messenger.send_to_user_package(
                messageManager.create_user_package(prefix, datetime.now().strftime("%H:%M:%S"), "Router reset started",
                                                   False))
            has_process_completed = self.__router_reset()

        else:
            data = self._command_not_found_string

        if data == self._command_not_found_string:
            has_process_completed = False
        package = messageManager.create_user_package(prefix, data, datetime.now().strftime("%H:%M:%S"),
                                                     has_process_completed)
        self.mcp.messenger.send_to_user_package(package)

        return

    # stops all loops so all threads can join the main thread
    def __shutdown_procedure(self) -> None:
        self.mcp.router.is_shut_down = True
        self.mcp.router.halt_module_execution = True
        self.mcp.messenger.is_shut_down = True
        self.mcp.event.set()  # wake up sleeping thread
        return

    # turns lights on/off
    def __lights(self, command: str) -> str:
        _, pwr = command.split(" ", 1)
        try:
            pwr = int(pwr)
        except:
            try:
                pwr = {"off": 0, "minimal": 1, "on": 1, "full": 100, "max": 100, "min": 1}[pwr]
            except:
                return self._command_not_found_string
        self.leds.set_power(pwr)
        return "lights on %d%% power" % self.leds.power

    def check_lights(self):
        if not self.mcp.is_host_pc:
            if self.leds.keep_safe():  # returns True if the power had to be decreased
                package = messageManager.create_user_package("mcp", "Turned light power down to prevent overheating",
                                                             datetime.now().strftime("%H:%M:%S"),
                                                             False)  # should this be this??? it should DEFINITELY not tell the system a command has finished whe this is sent halfway through
                self.mcp.messenger.send_to_user_package(package)

    # returns information on available commands
    def __help(self) -> str:
        text = " MCP commands that need no prefix:\n"
        text += " terminate:        force stops execution of the program immediately:\n"
        text += " shutdown:         stops execution safely by stopping all threads:\n"
        text += " restart:          stops execution safely and restarts the program:\n"
        text += " lightsON or OFF:  turns lights on or off respectively:\n"
        text += " cameraON or OFF:  turns camera on or off respectively:\n"
        text += " reset:            kills current process and restarts all modules and router\n"

        return text

    # in case router of router error hold all module processes and reset all attributes (including modules)
    def __router_reset(self) -> bool:
        # find thread
        for thread in self.mcp.threads:
            if thread.name == "RouterThread":
                # set to off and wait
                self.mcp.router.halt_module_execution = True
                self.mcp.router.is_shut_down = True
                while thread.is_alive():
                    time.sleep(1)
                # remove thread and clear router object and give feedback
                self.mcp.threads.remove(thread)
                self.mcp.router.clear_modules_list()

                self.setup_router_thread().start()
                break
        return True

    # Setup threads methods
    def setup_non_restartable_threads(self) -> None:
        listen_to_user_thread = threading.Thread(target=self.mcp.messenger.listen_to_user)
        listen_to_user_thread.setName("UserInputThread")
        self.mcp.threads.append(listen_to_user_thread)

        status_thread = threading.Thread(target=self.mcp.messenger.status_loop)
        status_thread.setName("StatusThread")
        self.mcp.threads.append(status_thread)

        return

    def setup_router_thread(self) -> threading.Thread:
        router_thread = threading.Thread(target=self.mcp.router.start)
        router_thread.daemon = True
        router_thread.setName("RouterThread")
        self.mcp.threads.append(router_thread)
        return router_thread
