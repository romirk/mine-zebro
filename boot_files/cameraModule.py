import cv2 as cv
import cameraApi
import os

class camera():
    def setup(self):
        self.camera = cv.VideoCapture(0)
        self.isOn = True
        self.takeScreenshot = False
        self.counter = 0
    

    def generateImage(self):
        while True:
            success, frame = self.camera.read()
            if (not success) or (not (self.isOn)):
                pass
            else:
                if(self.takeScreenshot):
                    self.takeScreenshot = False
                    path = os.getcwd()
                    cv.imwrite(path+'\\screenshots\\pic'+str(self.counter)+'.jpg', frame)
                    self.counter += 1
                ret, buffer = cv.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n' 
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def screenshot(self):
        #this command enables the user to take a screen shot of the current frame which is 
        self.takeScreenshot = True
    
    def off(self):
        self.isOn = False
    
    def on(self):
        self.isOn = True

    def readCommand(self, command):
        command = command.split()
        if(command[1] == 'on'):
            self.on()
        elif(command[1] == 'off'):
            self.off()
        elif(command[1] == 'screenshot'):
            self.screenshot()


# if __name__ == "__main__":

#     cap = cv.VideoCapture(0)
#     if not cap.isOpened():
#         print("Cannot open camera")
#         exit()
#     while True:
#         # Capture frame-by-frame
#         ret, frame = cap.read()
#         # if frame is read correctly ret is True
#         if not ret:
#             print("Can't receive frame (stream end?). Exiting ...")
#             break
#         # Our operations on the frame come here
#         gray = cv.cvtColor(frame, cv.COLOR_BGR)
#         # Display the resulting frame
#         cv.imshow('frame', gray)
#         if cv.waitKey(1) == ord('q'):
#             break
#     # When everything done, release the capture
#     cap.release()
#     cv.destroyAllWindows()
