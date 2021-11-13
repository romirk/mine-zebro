import threading
import time

import rinzler
from datetime import datetime

# Class holds mcp functionality relating to handling commands, setting up threads
# Note all methods that receive parameters from commands check if they are valid and if not send respond back to the user
from boot_files import messageManager


class McpHelper:
    _command_not_found_string = "MCP command does not exist"

    def __init__(self, mcp) -> None:
        self.mcp = mcp

    def handle_command(self, prefix: str, command: str) -> None:
        data = ""
        has_process_completed = True
        if command == "terminate":
            self.mcp.internal_state = rinzler.State.Terminate.value

        elif command == "shutdown":
            self.__shutdown_procedure()
            self.mcp.internal_state = rinzler.State.ShutDown.value

        elif command == "halt":
            self.mcp.router.halt_module_execution = True

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
        self.mcp.router.is_shut_down = True
        self.mcp.router.halt_module_execution = True
        self.mcp.messenger.is_shut_down = True
        self.mcp.cameraManager.is_shut_down = True
        return

    # turns lights on/off
    def __lights(self, command: str) -> str:
        # TODO add lights functionality
        if command == "lightsOn".lower():
            return "lights" + str(True)
        elif command == "lightsOff".lower():
            return "lights" + str(False)
        else:
            return self._command_not_found_string

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
        text += " reset:            resets all modules and router flags\n"

        return text

    # change how often a frame is taken from the camera and send to comms
    def __change_frame_period(self, command: str) -> str:
        try:
            time = command.split("fp=")[1]
            self.mcp.cameraManager.time_between_frames = float(time)
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
    def setup_non_restartable_threads(self, status_sleep_interval: float) -> None:
        listen_to_user_thread = threading.Thread(target=self.mcp.messenger.listen_to_user)
        listen_to_user_thread.setName("UserInputThread")
        self.mcp.threads.append(listen_to_user_thread)

        status_thread = threading.Thread(target=self.mcp.messenger.status_loop,
                                         args=(status_sleep_interval,))
        status_thread.setName("StatusThread")
        self.mcp.threads.append(status_thread)

        return

    def setup_router_thread(self) -> threading.Thread:
        router_thread = threading.Thread(target=self.mcp.router.start)
        router_thread.daemon = True
        router_thread.setName("RouterThread")
        self.mcp.threads.append(router_thread)
        return router_thread

    def setup_camera_thread(self) -> threading.Thread:
        camera_thread = threading.Thread(target=self.mcp.cameraManager.listen_to_camera)
        camera_thread.daemon = True
        camera_thread.setName("CameraThread")
        self.mcp.threads.append(camera_thread)
        return camera_thread
