from abc import ABC
import commsApi
import serverApi

from flask import Flask, render_template
from flask_classful import FlaskView
from flask_socketio import SocketIO




#This is a route/path defined by flask API.
#We use this view to initialize the connection with a HTTP get request by the client. 
class ControllerView(FlaskView):
    route_base = '/control/'

    #This method is called on the first HTTP Get request by the client. The html file is sent to the user
    #Note: Within the html file, Flask specific notation is used to define javascript and css files in the html document.
    #Check how main.js has been implemented for a concrete idea on how it works. 
    def index(self):
        return render_template('index.html')


#The submodule is used to setup the flask app and websocket connections. 
class CommunicationModule(commsApi.AbstractComms):

    def setup(self):
        self.__app = Flask(__name__)

        #registering the views
        ControllerView.register(self.__app)
    
        self.__app.config['SECRET_KEY'] = 'secret!'
        self.__socketio = SocketIO(self.__app)
        

        #Defining the different types of messages.
        @self.__socketio.on('message')
        def handle_message(info):
            print('recieved message: ' , info)
            self.__data = info

        self.__socketio.run(self.__app)
        
    def cin(self):
        return self.__data

    def cout(self, string):
        print("output>" + string)




if __name__ == '__main__':
    comms = CommunicationModule()
    comms.setup()