from abc import ABC
import commsApi


#Module responsible for communication with user
class CommsDummyManager(commsApi.AbstractComms):

    def setup(self):
        return

    def get_user_input(self):
        return input("rinzler>")

    def send_response(self, response):
        print("\noutput>" + response)
