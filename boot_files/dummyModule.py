import time
from abc import ABC
import module


class DummyManager(module.Module):

    def set_router(self, router):
        super().set_router(router)
        pass

    def get_id(self):
        return "dummy"

    def send_to_mcp(self, data, error):
        super().send_to_mcp(data, error)

    def check_if_hold(self):
        return super().check_if_hold()

    def command_does_not_exist(self, command):
        super().command_does_not_exist(command)
        pass

    def execute(self, command):
        super().execute(command)
        number = 0
        if (command == "count"):
            for i in range(5):
                data = str(i)
                self.send_to_mcp(data, 0)
                i += 1
        elif (command == "infinity"):
            while not self.check_if_hold():
                data = str(number)
                self.send_to_mcp(data, 0)
                number += 1
                time.sleep(5)
        else:
            self.command_does_not_exist(command)
        return
