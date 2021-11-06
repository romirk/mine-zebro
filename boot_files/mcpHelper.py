import rinzler
from datetime import datetime


class McpCommandHandler:

    def __init__(self, mcp):
        self.mcp = mcp

    def execute(self, command):
        if command == "terminate":
            self.mcp.internal_state = rinzler.State.Terminate.value

        elif command == "shutdown":
            self.__shutdown_procedure()
            self.mcp.internal_state = rinzler.State.ShutDown.value

        elif command == "hold":
            self.mcp.router.hold_module_execution = True

        elif command.startswith("lights"):
            self.__lights(command)

        elif command == "help":
            self.mcp.messenger.send_to_user_text(self.__help())

        elif command == "restart":
            self.__shutdown_procedure()
            self.mcp.internal_state = rinzler.State.Restart.value

        else:
            self.mcp.messenger.send_to_user_text("MCP command does not exist")

        return

    def __shutdown_procedure(self):
        self.mcp.messenger.send_to_user_package("shuttingDown", datetime.now().strftime("%H:%M:%S"), 0, True)
        self.mcp.router.is_shut_down = True
        self.mcp.router.hold_module_execution = True
        self.mcp.messenger.is_shut_down = True
        return

    def __lights(self, command):
        # TODO add lights functionality
        if command == "lightsOn".lower():
            self.mcp.messenger.send_to_user_text("lights" + str(True))
        elif command == "lightsOff".lower():
            self.mcp.messenger.send_to_user_text("lights" + str(False))
        else:
            self.mcp.messenger.send_to_user_text("MCP command does not exist")

    def __help(self):
        text = " MCP commands that need no prefix:\n"
        text += " terminate:        force stops execution of the program immediately:\n"
        text += " shutdown:         stops execution safely by stopping all threads:\n"
        text += " hold:             stops execution of active module safely:\n"
        text += " lightsON or OFF:  turns lights on or off respectively:\n"

        return text
