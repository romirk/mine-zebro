import commsApi


#comms Implementation using the terminal as input/package
class CommsDummyManager(commsApi.AbstractComms):

    def setup(self):
        return

    def cin(self):
        return input("rinzler>")

    def cout(self, package):
        print("output>" + str(package))
