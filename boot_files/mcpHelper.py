import threading
import time

import rinzler
from datetime import datetime

#Class holds mcp functionality relating to handling commands, setting up threads
#Note all methods that receive parameters from commands check if they are valid and if not send respond back to the user

class McpHelper:
    _command_not_found_string = "MCP command does not exist"

    def __init__(self, mcp):
        self.mcp = mcp

    def handle_command(self, command):
        if command == "terminate":
            self.mcp.internal_state = rinzler.State.Terminate.value
            return

        elif command == "shutdown":
            self.__shutdown_procedure()
            self.mcp.internal_state = rinzler.State.ShutDown.value
            return

        elif command == "hold":
            self.mcp.router.hold_module_execution = True
            return

        elif command.startswith("lights"):
            self.__lights(command)
            return

        elif command == "help":
            self.mcp.messenger.send_to_user_text(self.__help())
            return

        elif command == "restart":
            self.__shutdown_procedure()
            self.mcp.internal_state = rinzler.State.Restart.value
            return

        elif command.startswith("fp="):
            self.__change_frame_period(command)
            return

        elif command.startswith("camera"):
            self.__camera(command)
            return

        elif command == "reset":
            self.__router_reset()
            return

        else:
            self.mcp.messenger.send_to_user_text(self._command_not_found_string)

        return

    #change how often a frame is taken from the camera and send to comms
    def __change_frame_period(self, command):
        try:
            time = command.split("fp=")[1]
            self.mcp.cameraManager.time_between_frames = float(time)
        except:
            self.mcp.messenger.send_to_user_text(self._command_not_found_string)
        return

    #stops all loops so all threads can join the main thread
    def __shutdown_procedure(self):
        self.mcp.messenger.send_to_user_package("shuttingDown", datetime.now().strftime("%H:%M:%S"), 0, True)
        self.mcp.router.is_shut_down = True
        self.mcp.router.hold_module_execution = True
        self.mcp.messenger.is_shut_down = True
        self.mcp.cameraManager.is_shut_down = True
        return

    #turns lights on/off
    def __lights(self, command):
        # TODO add lights functionality
        if command == "lightsOn".lower():
            self.mcp.messenger.send_to_user_text("lights" + str(True))
        elif command == "lightsOff".lower():
            self.mcp.messenger.send_to_user_text("lights" + str(False))
        else:
            self.mcp.messenger.send_to_user_text(self._command_not_found_string)

    #returns information on available commands
    def __help(self):
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

    def setup_router_thread(self):
        router_thread = threading.Thread(target=self.mcp.router.start)
        router_thread.daemon = True
        router_thread.setName("RouterThread")
        self.mcp.threads.append(router_thread)
        return router_thread

    def setup_camera_thread(self):
        camera_thread = threading.Thread(target=self.mcp.cameraManager.listen_to_camera)
        camera_thread.daemon = True
        camera_thread.setName("CameraThread")
        self.mcp.threads.append(camera_thread)
        return camera_thread

    #turns camera on/off
    def __camera(self, command):
        if command == "cameraOn".lower():
            self.mcp.cameraManager.is_shut_down = False
            self.setup_camera_thread().start()

        elif command == "cameraOff".lower():
            #find thread
            for thread in self.mcp.threads:
                if thread.name == "CameraThread":
                    #set to off and wait
                    self.mcp.cameraManager.is_shut_down = True
                    while thread.is_alive():
                        time.sleep(1)
                    #remove and give feedback
                    self.mcp.threads.remove(thread)
            self.mcp.messenger.send_to_user_text("camera is off")
            return
        else:
            self.mcp.messenger.send_to_user_text(self._command_not_found_string)

    #in case router of router error hold all module processes and reset all attributes (including modules)
    def __router_reset(self):
        #find thread
        for thread in self.mcp.threads:
            if thread.name == "RouterThread":
                #set to off and wait
                self.mcp.router.hold_module_execution = True
                self.mcp.router.is_shut_down = True
                self.mcp.messenger.send_to_user_text("router reset started")
                while thread.is_alive():
                    time.sleep(1)
                #remove thread and clear router object and give feedback
                self.mcp.threads.remove(thread)
                self.mcp.router.clear_modules_list()

                self.setup_router_thread().start()
                self.mcp.messenger.send_to_user_text("router reset successful")
                break
        return

    def setup_non_restartable_threads(self):
        listen_to_user_thread = threading.Thread(target=self.mcp.messenger.listen_to_user)
        listen_to_user_thread.setName("UserInputThread")
        self.mcp.threads.append(listen_to_user_thread)

        in_out_thread = threading.Thread(target=self.mcp.input_output_loop)
        in_out_thread.setName("In/OutThread")
        self.mcp.threads.append(in_out_thread)

        status_thread = threading.Thread(target=self.mcp.status_loop)
        status_thread.setName("StatusThread")
        self.mcp.threads.append(status_thread)

        return