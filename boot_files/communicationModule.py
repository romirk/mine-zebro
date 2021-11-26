from abc import ABC
from logging import info
import commsApi
from threading import Thread
import json
<<<<<<< HEAD
import cameraModule
=======
import cameraDummy
>>>>>>> user-interface
# import serverApi

from flask import Flask, render_template, Response
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
        # return render_template('index.html')
        return 
    
    


#The submodule is used to setup the flask app and websocket connections. 
class CommunicationModule(commsApi.AbstractComms):
    

    def setup(self):
        self.__app = Flask(__name__, static_folder="../MineRoverInterface/MineRoverInterface/rover-interface/build", static_url_path="/")
        self.__data = ""
        self.received = False
        self.lock = False
        #registering the views
        # ControllerView.register(self.__app)
        
        #create a camera module instance
        self.camera = cameraModule.camera()
        self.camera.setup()

    
        self.__app.config['SECRET_KEY'] = 'secret!'
        self.__socketio = SocketIO(self.__app)
        
        # Preparing for creating a thread for the application. 
<<<<<<< HEAD

        #Defining the application routes
        @self.__app.route('/video_feed')
        def video_feed():
            if(self.camera.isOn):
                return Response(self.camera.generateImage(),mimetype='multipart/x-mixed-replace; boundary=frame')
            



=======
        @self.__app.route("/")
        def index():
            return self.__app.send_static_file('index.html')
                    
>>>>>>> user-interface

        #Defining the incoming command.
        @self.__socketio.on('command')
        def handle_command(command):
            #Note command is a dictionary object.
            # data = json.load(command)

            if(self.received == False):
                if(command["command"].startswith('camera')):
                    self.camera.readCommand(command["command"])
                else:    
                    self.__data = command["command"]
                    self.received = True
           
            print(self.__data)


        #Defining the different types of messages.
        @self.__socketio.on('message')
        def handle_message(info):
            print('recieved message: ' , info)
            self.__data = info

        kwargs = {'app' : self.__app}

        serverThread = Thread(target=self.__socketio.run, daemon=True, kwargs=kwargs).start()
        # self.__socketio.run(self.__app)
        # print("TESTING")
        
    def cin(self):
        if(self.received):
            self.received = False
            return self.__data
        return ""

    
    def cout(self, string):
        self.__socketio.emit('output', string)
        print("output>" + string)




if __name__ == '__main__':
    comms = CommunicationModule()
    comms.setup()