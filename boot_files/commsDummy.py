import commsApi


#comms Implementation using the terminal as input/output
class CommsDummyManager(commsApi.AbstractComms):

    def setup(self):
        return

    def cin(self):
        return input("rinzler>")

    def cout(self, string):
        print("output>" + string)
