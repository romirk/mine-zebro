import time
import module


# Example of module class
class DummyManager(module.Module):

    def __init__(self, output_array):
        super().__init__(output_array)
        pass

    def get_id(self):
        return "dummy"

    def help(self):
        text = super().help()
        text += " count: Count from 0-4 with rests in between\n"
        text += " loop:  Count from 0 until hold command given\n"
        self.send_to_mcp(text)
        pass

    def execute(self, command):
        super().execute(command)
        number = 0
        if command == "count":
            for i in range(5):
                data = str(i)
                self.send_to_mcp(data)
                i += 1

        elif command == "loop":
            while not self.check_if_hold():
                data = str(number)
                self.send_to_mcp(data)
                number += 1
                time.sleep(5)

        elif command == "help":
            self.help()

        else:
            self.command_does_not_exist(command)
        return

    def send_to_mcp(self, output):
        super().send_to_mcp(output)

    def check_if_hold(self):
        return super().check_if_hold()

    def command_does_not_exist(self, command):
        super().command_does_not_exist(command)
        pass
