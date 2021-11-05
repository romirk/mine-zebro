from abc import ABC
import commsApi


#Module responsible for communication with user
class CommsDummyManager(commsApi.AbstractComms):

    def setup(self):
        return

    def cin(self):
        return input("rinzler>")

    def cout(self, string):
        print("output>" + string)
