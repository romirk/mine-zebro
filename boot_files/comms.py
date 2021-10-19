# Dummy comms for testing
from abc import ABC

import module


class CommsManager(module.Module):

    def get_id(self):
        return "Comms"

    def setup(self):
        print("Comms function")
        return
