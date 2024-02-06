# Creating interface to contact message server and send request for registering our group
import zmq
from datetime import datetime
from threading import Thread
import netifaces as ni

THREAD_COUNT = 5

users = set() # list of users in the group, users will be identified by uuid
userMsg = {} # key: timestamp, value: [userUUID, message]
groupName = None

def worker_thread(context=None):
	print("Worker thread started")
	"""
	worker thread to handle the request from the user
	"""
	context = context or zmq.Context.instance()
	socket = context.socket(zmq.REP)
	socket.connect("inproc://workers")
	# four type of request can be made to the group by the user
	# 1. message send -> acceptUserMessageRequest()
	# 2. message get -> userGetMessageRequest()
	# 3. join -> acceptUserJoinRequest()
	# 4. leave -> acceptUserLeaveRequest()
	while True:
		request = socket.recv_string()
		request = request.split()
		print(f"Request: {request}")

		if request[0] == "JOIN":
			# message = "JOIN " + userUUID
			acceptUserJoinRequest(socket, request[1])
		elif request[0] == "LEAVE":
			# message = "LEAVE " + userUUID
			acceptUserLeaveRequest(socket, request[1])
		elif request[0] == "SEND":
			# message = "SEND " + userUUID + " " + message
			acceptUserMessageRequest(socket, request[1], request[2:])
		elif request[0] == "GET":
			# message = "GET " + userUUID + " " + timestamp
			userGetMessageRequest(socket, request[1], request[2])
		else:
			socket.send_string("FAIL")

# GROUP REGISTRATION FUNCTION
			
def groupRegisterRequest(groupName, groupIP, groupPort, msgServerIP="localhost"):
	"""
	register the group with the message server on port 5555
	"""
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect(f"tcp://{msgServerIP}:5555")

	socket.send_string(f"REGISTER {groupName} {groupIP} {groupPort}")
	message = socket.recv()
	print(f"{message}")
	socket.close()


# USER FUNCTIONS
	
def acceptUserJoinRequest(socket, userUUID):
	global users
	if userUUID in users:
		socket.send_string("FAIL")
		return
	users.add(userUUID)
	print(f"Join Request from {userUUID}")
	socket.send_string("SUCESS")

def acceptUserLeaveRequest(socket, userUUID):
	global users
	if userUUID not in users:
		socket.send_string("FAIL")
		return
	users.remove(userUUID)
	print(f"Leave Request from {userUUID}")
	socket.send_string("SUCESS")

def acceptUserMessageRequest(socket, userUUID, message):
	"""
	accepts a message from the user and stores it in the memory for future retrieval
	"""
	global userMsg
	if userUUID not in users:
		socket.send_string("FAIL")
		return
	print(f"Message send from {userUUID}")
	msg = [userUUID, message]
	userMsg[datetime.now()] = msg
	socket.send_string("SUCESS")

def userGetMessageRequest(socket, userUUID, reqTimestamp):
	"""
	send all the messages in the group that are newer than the timestamp
	"""
	global userMsg
	if userUUID not in users:
		socket.send_string("FAIL")
		return
	print(f"Get message request from {userUUID}")
	messages = []
	for key, value in userMsg.items():
		user_timestamp = datetime.strptime(reqTimestamp, "%H:%M:%S")
		if key >= user_timestamp:
			messages.append(value)
	socket.send_pyobj(messages)

def main():
	groupName = input("Enter the group name: ")
	interface = input("Enter the interface name: ")
	groupIP = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
	groupPort = int(input("Enter the port number: "))
	
	# register the group with the message server
	groupRegisterRequest(groupName, groupIP, groupPort)
	print("Group registered")
	context = zmq.Context.instance()
	clients = context.socket(zmq.ROUTER) 
	clients.bind(f"tcp://*:{int(groupPort)}")
	workers = context.socket(zmq.DEALER)
	workers.bind("inproc://workers")
	zmq.device(zmq.QUEUE, clients, workers)
	print("Device started")
	for i in range(THREAD_COUNT):
		Thread(target=worker_thread).start()

	

	#TODO:
	#	register the group with the message server
	# 	groupRegisterRequest(socket, groupName, groupIP, groupPort)

if __name__ == "__main__":
	# main()
	groupName = input("Enter the group name: ")
	interface = input("Enter the interface name: ")
	groupIP = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
	groupPort = int(input("Enter the port number: "))
	
	# register the group with the message server
	groupRegisterRequest(groupName, groupIP, groupPort)
	print("Group registered")
	context = zmq.Context.instance()
	clients = context.socket(zmq.ROUTER) 
	clients.bind(f"tcp://127.0.0.1:{int(groupPort)}")
	workers = context.socket(zmq.DEALER)
	workers.bind("inproc://workers")
	print("Device started")
	for i in range(THREAD_COUNT):
		Thread(target=worker_thread).start()
	zmq.device(zmq.QUEUE, clients, workers)

