import commsApi


#comms Implementation using the terminal as input/package
class CommsDummyManager(commsApi.AbstractComms):

    def setup(self) -> None:
        return

    def cin(self) -> str:
        return input("rinzler>")

    def cout(self, package:dict) -> None:
        print("output>" + str(package))
