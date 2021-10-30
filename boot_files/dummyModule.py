import time
from abc import ABC
import module


class DummyManager(module.Module):

    def get_id(self):
        return "Dummy"

    def execute(self, command, router):
        super().execute(command, router)
        while not self.check_if_hold(router):
            data = command
            self.send_to_mcp(router, data, 0)
            time.sleep(5)
        return

    def send_to_mcp(self, router, data, error):
        super().send_to_mcp(router, data, error)

    def check_if_hold(self, router):
        super().check_if_hold(router)

