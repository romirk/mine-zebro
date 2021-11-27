import multiprocessing
import threading
import time
from datetime import datetime

import rinzler
from router import Str

try:
    from leds import LEDs
except:
    LEDs = int

# Class holds mcp functionality relating to handling commands, setting up threads
# Note all methods that receive parameters from commands check if they are valid and if not send respond back to the user
import messageManager, router


class McpHelper:
    _command_not_found_string = "MCP command does not exist"

    def __init__(self, mcp) -> None:
        self.mcp = mcp
        #setting up some important multithreading objects
        self.manager = multiprocessing.Manager()
        self.mcp.event = self.manager.Event()
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

        elif command == "halt":
            self.mcp.router_data[router.Str.is_halt.value] = True

        elif command.startswith("lights"):
            data = self.__lights(command)

        elif command == "help":
            data = self.__help()

        elif command == "restart":
            self.__shutdown_procedure()
            self.mcp.internal_state = rinzler.State.Restart.value

        elif command.startswith("fp="):
            data = self.__change_frame_period(command)

        elif command.startswith("camera"):
            data = self.__camera(command)

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
        self.mcp.router_data[router.Str.is_shut_down.value] = True
        self.mcp.router_data[router.Str.is_halt.value] = True
        self.mcp.messenger.is_shut_down = True
        self.mcp.cameraManager.is_shut_down = True
        return

    # turns lights on/off
    def __lights(self, command: str) -> str:
        _, pwr = command.split(" ", 1)
        if pwr in ("0", "off"):
            if not self.mcp.is_host_pc:
                self.leds.set_power(0)
            return "lights off"
        elif pwr in ("1", "on"):
            if not self.mcp.is_host_pc:
                self.leds.set_power(1)
            return "lights on on lowest setting"
        elif pwr == "2":
            if not self.mcp.is_host_pc:
                self.leds.set_power(2)
            return "lights on on 2nd power setting"
        elif pwr == "3":
            if not self.mcp.is_host_pc:
                self.leds.set_power(3)
            return "lights on on 3nd power setting"
        elif pwr == "4":
            if not self.mcp.is_host_pc:
                self.leds.set_power(4)
            return "lights on on 4th (maximum) power setting"
        else:
            return self._command_not_found_string

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
        text += " hold:             stops execution of active module safely:\n"
        text += " lightsON or OFF:  turns lights on or off respectively:\n"
        text += " cameraON or OFF:  turns camera on or off respectively:\n"
        text += " fp=:              change the period between each frame (in seconds)\n"
        text += " reset:            kills current process and restarts all modules and router\n"

        return text

    # change how often a frame is taken from the camera and send to comms
    def __change_frame_period(self, command: str) -> str:
        try:
            period = command.split("fp=")[1]
            self.mcp.cameraManager.time_between_frames = float(period)
            return ""
        except:
            return self._command_not_found_string

    # turns camera on/off
    def __camera(self, command: str) -> str:
        if command == "cameraOn".lower():
            self.mcp.cameraManager.is_shut_down = False
            self.setup_camera_thread().start()
            return "Camera is on"

        elif command == "cameraOff".lower():
            # find thread
            for thread in self.mcp.threads:
                if thread.name == "CameraThread":
                    # set to off and wait
                    self.mcp.cameraManager.is_shut_down = True
                    while thread.is_alive():
                        time.sleep(1)
                    # remove and give feedback
                    self.mcp.threads.remove(thread)
            return "Camera is off"
        else:
            return self._command_not_found_string

    # in case router of router error hold all module processes and reset all attributes (including modules)
    def __router_reset(self) -> bool:
        # find thread
        for thread in self.mcp.threads:
            if thread.name == "RouterThread":
                thread.kill()
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

    def setup_router_thread(self) -> multiprocessing.Process:

        self.mcp.routerLock = self.manager.Lock()

        self.mcp.router_data = self.manager.dict()
        self.mcp.router_data[Str.lock.value] = self.mcp.routerLock
        self.mcp.router_data[Str.event.value] = self.mcp.event
        self.mcp.router_data[Str.is_shut_down.value] = False
        self.mcp.router_data[Str.is_halt.value] = False
        self.mcp.router_data[Str.is_command_loaded.value] = False
        self.mcp.router_data[Str.is_package_ready.value] = False
        self.mcp.router_data[Str.prefix.value] = ""
        self.mcp.router_data[Str.command.value] = ""
        self.mcp.router_data[Str.package.value] = dict

        router_thread = multiprocessing.Process(target=router.start, args=(self.mcp.router_data,))
        router_thread.daemon = True
        router_thread.name = "RouterThread"
        self.mcp.threads.append(router_thread)
        return router_thread

    def setup_camera_thread(self) -> threading.Thread:
        camera_thread = threading.Thread(target=self.mcp.cameraManager.listen_to_camera)
        camera_thread.daemon = True
        camera_thread.setName("CameraThread")
        self.mcp.threads.append(camera_thread)
        return camera_thread
