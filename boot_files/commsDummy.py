from abc import ABC
import commsApi


#Module responsible for communication with user
class CommsDummyManager(commsApi.AbstractComms):

    def start(self):
        return

    def get_user_input(self):
        return input("Input command")

    def send_response(self, response):
        print(response)
