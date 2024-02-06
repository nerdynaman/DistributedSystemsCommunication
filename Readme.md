# Using ZeroMQ to Low-Level Group Messaging Application

## Introduction
We create a simple low-level group messaging application using ZeroMQ. The application is a simple chat application that allows multiple clients to connect to a server and send messages to each other. The server is a simple application that listens for incoming messages and forwards them to all connected clients. The clients are simple applications that connect to the server and send messages to the server. The server then forwards the messages to all connected clients.

## Groups
ports: TBD by the group owner
## Message server
**port**: 5555

## Users
**port**: they don't have a port as they are not listening for incoming messages initially. 