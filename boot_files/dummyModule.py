import time
from abc import ABC
import module


class DummyManager(module.Module):

    def get_id(self):
        return "dummy"

    def execute(self, command, router):
        super().execute(command, router)
        number = 0
        if (command == "count"):
            for i in range(5):
                data = str(i)
                self.send_to_mcp(router, data, 0)
                i += 1
        elif (command == "infinity"):
            while not self.check_if_hold(router):
                data = str(number)
                self.send_to_mcp(router, data, 0)
                number += 1
                time.sleep(5)
        return

    def send_to_mcp(self, router, data, error):
        super().send_to_mcp(router, data, error)

    def check_if_hold(self, router):
        super().check_if_hold(router)

