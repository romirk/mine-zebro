# Dummy comms for testing
from abc import ABC

import module


class CommsManager(module.Module):

    def execute(self, command):
        pass

    def get_id(self):
        return "Comms"

    def setup(self):
        print("Comms function")
        return
