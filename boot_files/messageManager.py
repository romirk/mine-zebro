import router


class MessageManager:

    # API used by MCP to communicate to Router
    def __init__(self, router):
        self.__router = router;

    #def send(self, data):
    #    prefix = self.get_prefix(data)
    #    self.__router.send
    # TODO

    # def receive(self, data):
    # TODO

    def get_prefix(self, data):
        return data.split(" ", 1).__getitem__(0)


if __name__ == '__main__':
    command = "loco go forward"
    messenger = MessageManager(1);
    print(messenger.get_prefix(command))
