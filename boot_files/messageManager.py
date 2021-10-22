import router

#Wrapper API for Router that acts as intermediate between McP and Router
class MessageManager:

    def __init__(self, router):
        self.__router = router;

    # Used to get destination module fo package
    def get_prefix(self, data):
        return data.split(" ", 1).__getitem__(0)

    # Unpack data from MCP and prepare to send it to router
    def send(self, data):
        prefix = self.get_prefix(data)
        self.__router.load_command(prefix,data)

    # def receive(self, data):
    # TODO



if __name__ == '__main__':
    command = "loco go forward"
    messenger = MessageManager(1);
    print(messenger.get_prefix(command))
