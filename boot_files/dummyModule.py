from abc import ABC
import module


class DummyManager(module.Module):

    def get_id(self):
        return "Dummy"

    def execute(self, command, router):
        super().execute(command, router)
        data = command
        self.send_to_mcp(router, data, 0)

    def send_to_mcp(self, router, data, error):
        super().send_to_mcp(router, data, error)
