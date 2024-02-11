import time
import zmq
from threading import Thread
import netifaces as ni
MESSAGE_SERVER_PORT = 5555

groups = {} #key: group name, value: group ip and port -> {'groupName'->UUID : ('groupIP'->IPaddr, groupPort->int)}

def registerGroup(socket, groupName, groupIP, groupPort):
    """
    Registers the group with the server
    """
    global groups
    if groupName in groups:
        socket.send_string("FAIL")
        return
    groups[groupName] = (groupIP, groupPort)
    print(f"JOIN REQUEST FROM {groupName} at {groupIP}:{groupPort}")
    socket.send_string("SUCESS")

def sendGroups(socket, userUUID):
    """
    user requests for the list of groups along with their ip and port
    format of arrray: [groupName, groupIP, groupPort]
    """
    print(f"GROUP LIST REQUEST FROM {userUUID}")
    arr=[]
    for key, value in groups.items():
        arr.append([key, value[0], value[1]])
    socket.send_pyobj(arr)


def main():
    interface = input("Enter the interface name: ")
    msgServerIP = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']

    context = zmq.Context.instance()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://{msgServerIP}:{MESSAGE_SERVER_PORT}")

    while True:
        message = socket.recv_string()
        if message.startswith("REGISTER"):
            _, groupName, groupIP, groupPort = message.split()
            registerGroup(socket, groupName, groupIP, int(groupPort))
        elif message.startswith("GET_GROUPS"):
            _, userUUID = message.split()
            sendGroups(socket, userUUID)
        else:
            socket.send_string("FAIL")

if __name__ == "__main__":
    main()