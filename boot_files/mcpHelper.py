import rinzler
from datetime import datetime


class McpCommandHandler:

    def __init__(self, mcp):
        self.mcp = mcp

    def execute(self, command):
        if command == "terminate":
            self.mcp.internal_state = rinzler.State.Terminate

        elif command == "shutdown":
            self.mcp.messenger.send_to_user_package("shuttingDown", datetime.now().strftime("%H:%M:%S"), 0, True)
            self.mcp.router.is_shut_down = True
            self.mcp.router.hold_module_execution = True
            self.mcp.messenger.is_shut_down = True
            self.mcp.internal_state = rinzler.State.ShutDown

        elif command == "hold":
            self.mcp.router.hold_module_execution = True

        elif command.startswith("lights"):
            # TODO add lights functionality
            if command == "lightsOn".lower():
                self.mcp.messenger.send_to_user_text("lights" + str(True))
            elif command == "lightsOff".lower():
                self.mcp.messenger.send_to_user_text("lights" + str(False))
            else:
                self.mcp.messenger.send_to_user_text("MCP command does not exist")

        else:
            self.mcp.messenger.send_to_user_text("MCP command does not exist")

        return
