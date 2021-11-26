import time

<<<<<<< HEAD
import module
=======
>>>>>>> user-interface

import module;
try: #prevent errors when testing on computer
    from smbus2 import SMBus
except: SMBus = int

# Example of module class
class DummyManager(module.Module):

    def __init__(self, router_obj, bus: SMBus = None):
        super().__init__(router_obj, bus)

    def setup(self):
        pass#super().setup()

    def get_id(self):
        return "dummy"

    def get_status(self):
        pass

    def help(self):
        text = super().help()
        text += " count: Count from 0-4 with rests in between\n"
        text += " loop:  Count from 0 until hold command given\n"
        return text#self.send_output(module.OutputCode.data.value, "", text)

    def execute(self, command):
        #super().execute(command)
        number = 0
        if command == "count":
            for i in range(5):
                data = str(i)
                self.send_output(self._data(data,"Counting"))
                i += 1

        elif command == "loop":
            while not super().check_halt_flag():
                data = str(number)
                self.send_output(code=module.OutputCode.data.value, msg="Counting", data=data)
                number += 1
                time.sleep(5)

        elif command == "help":
            self.send_output(self._info(self.help()))

        elif command == "battery":
            self.send_output(code=module.OutputCode.warning.value, msg="Battery %")

        elif command == "motors":
            self.send_output(code=module.OutputCode.warning.value, msg="Motors are fine")

        else:
            self.send_output(self.invalid_command())
        return
