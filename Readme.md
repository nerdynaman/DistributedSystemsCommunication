# Using ZeroMQ to Low-Level Group Messaging Application

## Introduction
We create a simple low-level group messaging application using ZeroMQ. The application is a simple chat application that allows multiple clients to connect to a server and send messages to each other. The server is a simple application that listens for incoming messages and forwards them to all connected clients. The clients are simple applications that connect to the server and send messages to the server. The server then forwards the messages to all connected clients.

## Groups
ports: TBD by the group owner
## Message server
**port**: 5555

## Users
**port**: they don't have a port as they are not listening for incoming messages initially. 

#### References

- [GPTchat](https://chat.openai.com/share/2884fc61-bf8d-4d0b-af85-622ed8952499)

Some questions that I have asked in the chat:
1) differfenece in using request response and client server socket type in zero mq
2) please elaborate on the use case of dealer
3) what does router type of socket does