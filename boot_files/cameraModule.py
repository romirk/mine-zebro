from cv2 import triangulatePoints


usePicamera = False

try:
    import cv2 as cv
except:
    import picamera
    usePicamera = True
import cameraApi
import os

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)




class camera():
    def setup(self):
        if(not usePicamera):
            self.camera = cv.VideoCapture(0)
        else:
            self.camera = picamera.PiCamera(resolution='640x480', framerate=24)
            self.output = StreamingOutput()
            camera.start_recording(self.output, format = 'mjpeg')

        self.isOn = True
        self.takeScreenshot = False
        self.counter = 0
    

    def generateImage(self):
        if(not usePicamera):
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
        else:
            while True:
                frame = self.output.frame
                if(self.takeScreenshot):
                    self.takeScreenshot = False
                    path = os.getcwd()
                    self.camera.capture(path+'\\screenshots\\pic'+str(self.counter)+'.jpg')
                    self.counter += 1

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
