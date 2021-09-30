# April 2018
# Jeffrey Miog

from multiprocessing.connection import Client
import time

DEBUG = 0

class locomotion_manager:
	SPEED_STOP = 0
	SPEED_FULL = 5
	SPEED_LAY_DOWN = 0
	SPEED_STAND_UP = 0

	DIRECTION_LEFT = 1
	DIRECTION_RIGHT = 9
	DIRECTION_STRAIGHT = 5
	DIRECTION_LAY_DOWN = 5
	DIRECTION_STAND_UP = 0

	def setup(self):
		#opening socket
		self.address = ('localhost', 6000)
		self.connection = Client(self.address, authkey = b'zebro')

	def flush_socket(self):
		garbage = self.connection.recv()
		return garbage

	def forwards(self):
		if(DEBUG): print("LOC: moving forwards")
		self.connection.send([int(self.SPEED_FULL), int(self.DIRECTION_STRAIGHT)])
		reply = self.connection.recv()
		if (DEBUG): print("LOC: reply from socket: " + str(reply))

	def backwards(self):
		if (DEBUG): print("LOC: moving backwards")

	# walk left for 1 step
	def left(self):
		if (DEBUG): print("LOC: moving left")
		self.connection.send([int(self.SPEED_STOP), int(self.DIRECTION_LEFT)])
		reply = self.connection.recv()
		if (DEBUG): print("LOC: reply from socket: " + str(reply))

	# walk right for 1 step
	def right(self):
		if (DEBUG): print("LOC: moving right")
		self.connection.send([int(self.SPEED_STOP), int(self.DIRECTION_RIGHT)])
		reply = self.connection.recv()
		if (DEBUG): print("LOC: reply from socket: " + str(reply))

	def lay_down(self):
		if (DEBUG): print("LOC: laying down")
		self.connection.send([int(self.SPEED_LAY_DOWN), int(self.DIRECTION_LAY_DOWN)])
		reply = self.connection.recv()
		if (DEBUG): print("LOC: reply from socket: " + str(reply))

	def stand_up(self):
		if (DEBUG): print("LOC standing up")
		self.connection.send([int(self.SPEED_STAND_UP), int(self.DIRECTION_STAND_UP)])
		reply = self.connection.recv()
		if (DEBUG): print("LOC reply from socket: " + str(reply))

	def coolDown(self, lay_time):
		return 0



#keep thread active in order to keep the socket open.
#closing the socket kills the locomotion-toplevelcontroller
#which is the controller for locomotion.
if __name__ == "__main__":
	#create locomotion instance
	locomotion = locomotion_manager()
	#setup the socket connection
	locomotion_manager.setup(locomotion)
	#walk straight for 1 steps
	delay_tijd = 0.1
	locomotion.stand_up()
	#time.sleep(delay_tijd*2)
	while(1):
		#testcase 1

		# print("LOC test 2")
		# print("LOC 2 standup")
		# locomotion.stand_up()
		# #time.sleep(delay_tijd)
		# print("LOC 2 forwards")
		locomotion.forwards()
		# #time.sleep(delay_tijd)
		# print("LOC 2 forwards")
		# locomotion.forwards()
		# #time.sleep(delay_tijd)
		# print("LOC 2 standup")
		# locomotion.stand_up()
		# #time.sleep(delay_tijd)
		# print("LOC 2 left")
		# locomotion.left()
		# #time.sleep(delay_tijd)
		# print("LOC 2 left")
		# locomotion.left()
		# #time.sleep(delay_tijd)
		# print("-------------")



