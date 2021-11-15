import time
import module

try: #prevent errors when testing on computer
    from smbus2 import SMBus
except: SMBus = int

# Example of module class
class DummyManager(module.Module):

    def __init__(self, router_obj, bus: SMBus = None):
        super().__init__(router_obj, bus)

    def setup(self):
        super().setup()

    def get_id(self):
        return "dummy"

    def get_status(self):
        pass

    def help(self):
        text = super().help()
        text += " count: Count from 0-4 with rests in between\n"
        text += " loop:  Count from 0 until hold command given\n"
        super().send_to_router(module.OutputCode.data.value, "", text)

    def execute(self, command):
        super().execute(command)
        number = 0
        if command == "count":
            for i in range(5):
                data = str(i)
                super().send_to_router(module.OutputCode.data.value, "Counting", data)
                i += 1

        elif command == "loop":
            while not super().check_halt_flag():
                data = str(number)
                super().send_to_router(module.OutputCode.data.value, "Counting", data)
                number += 1
                time.sleep(5)

        elif command == "help":
            self.help()

        elif command == "battery":
            super().send_to_router(module.OutputCode.warning.value, "Battery %")

        elif command == "motors":
            super().send_to_router(module.OutputCode.warning.value, "Motors are fine")

        else:
            super().command_does_not_exist(command)
        return
