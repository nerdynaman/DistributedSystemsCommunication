import uuid
from datetime import datetime
import zmq

groups = {} #key: group name, value: group ip and port -> {'groupName'->UUID : ('groupIP'->IPaddr, groupPort->int)}
loggedGroups = set() # set of groups the user has joined
userUUID = str(uuid.uuid4())

def getGroups():

	"""
	user requests for the list of groups along with their ip and port from the message server
	format of array recieved: [ [groupName, groupIP, groupPort], [groupName, groupIP, groupPort], ...]
	"""

	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect("tcp://localhost:5555")

	global groups
	socket.send_string(f"GET_GROUPS {userUUID}")
	groupRecieved = socket.recv_pyobj()
	i = 1
	for group in groupRecieved:
		groups[group[0]] = (group[1], group[2])
		if f"{group[1]}-{group[2]}" in loggedGroups:
			print(f"Group {i}: {group[0]} at {group[1]}:{group[2]} (Joined)")
		else:
			print(f"Group {i}: {group[0]} at {group[1]}:{group[2]}")
		i += 1

	socket.close()


def sendMessage(socket, message):
	"""
	send a message to the group
	"""
	socket.send_string(f"SEND {userUUID} {message}")
	response = socket.recv_string()
	# print("DEBUG response is: ", response)
	if response == "SUCESS": 
		print("SUCESS")
	else:
		print("Failed to send message")

def leaveGroup(socket):
	"""
	leave the group
	"""
	socket.send_string(f"LEAVE {userUUID}")
	response = socket.recv_string()
	if response == "SUCESS":
		print("SUCESS")
	else:
		print("Failed to leave group")

def getMessages(socket):
	"""
	get the messages from the group
	"""
	timestamp = input("Enter the timestamp from which you want to recieve the messages(HH:MM:SS): ")
	if not timestamp:
		timestamp = "00:00:00"
	socket.send_string(f"GET {userUUID} {timestamp}")
	messages = socket.recv_pyobj()
	for message in messages:
		print(f"{message[0]}: {message[1]}")
		

def groupInterface(socket):
	"""
	Menu Interface for the user after joining a group
	"""
	while True:
		print("1. Send a message")
		print("2. Leave the group")
		print("3. Recieve messages")
		print("4. Exit")
		choice = int(input())
		if choice == 1:
			print("Enter the message: ")
			message = input()
			sendMessage(socket, message)
		elif choice == 2:
			leaveGroup(socket)
			return main()
		elif choice == 3:
			getMessages(socket)
		elif choice == 4:
			socket.close()
			return main()
		else:
			print("Invalid choice")


def joinGroup():
	"""
	Join a group by entering the group number
	"""
	global loggedGroups
	print("Enter the group number you want to join: ")
	groupNumber = int(input())
	groupName = list(groups.keys())[groupNumber - 1]
	groupIP, groupPort = groups[groupName]
	print(f"Joining {groupName} at {groupIP}:{groupPort}")
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect(f"tcp://{groupIP}:{groupPort}")
	socket.send_string(f"JOIN {userUUID}")
	message = socket.recv_string()
	if message == "SUCESS":
		print(f"SUCESS")
		loggedGroups.add(f"{groupIP}-{groupPort}")
		return groupInterface(socket)
	else:
		print("Failed to join the group")

def resumeSession():
	"""
	Resume the session of the user
	"""
	ch = input("Do you want to view the groups? (y/n): ")
	if ch == "y":
		getGroups()
	groupNumber = int(input("Enter the group number you want to resume: "))
	groupName = list(groups.keys())[groupNumber - 1]
	groupIP, groupPort = groups[groupName]
	print(f"Resuming {groupName} at {groupIP}:{groupPort}")
	context = zmq.Context()
	socket = context.socket(zmq.REQ)
	socket.connect(f"tcp://{groupIP}:{groupPort}")
	# We don't need to send the JOIN request again as the user is already a part of the group
	return groupInterface(socket)


def main():
	print(f"Welcome {userUUID}")
	print("Kindly read the options and enter the number of the option you want to select")
	print("1. Get the list of groups")
	print("2. Join a group")
	print("3. Resume the existing session")
	print("4. Exit")
	while True:
		print("Enter your choice: ",end=" ")
		choice = int(input())
		if choice == 1:
			getGroups()
		elif choice == 2:
			joinGroup()
		elif choice == 3:
			resumeSession()
		elif choice == 4:
			exit()
		else:
			print("Invalid choice")

if __name__ == "__main__":
	main()