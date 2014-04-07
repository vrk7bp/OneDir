#!/usr/bin/env python

"""
TCP file client using Twisted.  The goal of this simple demo was to show:
a) How JSON string can be used to send complex data (lists, dictionaries)
b) How this could be used to send commands and data to go with those commands
c) how the server could be made recognize commands and be structured to handle them.

(NOTE: This is just a demo.  It's not necessarily a great design. It's to show how
something might be done.)

3rd party libraries need to be installed to run this!  Use pip to install:
a) Twisted

How to run these.  (Might be easier to run these from the command-line.)
a) Start the server, file1_server_tw.py.
b) Start the client, this program, on the same computer. (In a different window.)
c) In the client, type a Python dictionary, where one key is "cmd" -- this could be
the "command" you're sending.  The server recognizes these commands: user, write, delete.
A method is called for each one of these, and right now the server just sends
back an acknowledgment and ignores other data in the dictionary.  But you can see how this
could be the start of implementing a protocol.
d) Hit return in the client to stop the client.
e) In the server window, Hit CTRL-C or whatever your operating system requires to kill a running program.

It should be possible to run these on two different computers.
Start the server on one machine.
When you start the client on the 2nd machine, give a command-line argument: the IP address
or full internet hostname of the server machine.


"""

from twisted.internet import protocol, reactor
import sys
import fileinput
import json

HOST = '127.0.0.1'
# HOST = '172.27.98.114'
PORT = 21567

class TSClntProtocol(protocol.Protocol):
    def sendData(self):
        """
        Our own method, does NOT override anything in base class.
        Get data from keyboard and send to the server.
        """
        data = raw_input('Enter JSON of command: ')
        if data:
            self.transport.write(str(data))
        else:
            self.transport.loseConnection() # if no data input, close connection

    def connectionMade(self):
        """ what we'll do when connection first made """
        self.sendData()

    def dataReceived(self, data):
        """ what we'll do when our client receives data """
        print "client received: ", data
        self.sendData()  # let's repeat: get more data to send to server

class TSClntFactory(protocol.ClientFactory):
    protocol = TSClntProtocol
    # next, set methods to be called when connection lost or fails
    clientConnectionLost = clientConnectionFailed = \
        lambda self, connector, reason: reactor.stop()  # version from book
        # lambda self, connector, reason: handleLostFailed(reason)

    # Heck, I had this working with the code just above this, so you didn't need
    # the lamba.  But then I broke it.  Will post a new version with a fix.
    def handleLostFailed1(self, reason):
        print 'Connection closed, lost or failed.  Reason:', reason
        reactor.stop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        HOST = sys.argv[1]
    print "Connecting to (HOST, PORT): ", (HOST, PORT)

    reactor.connectTCP(HOST, PORT, TSClntFactory())
    reactor.run()

    filename = "files.txt"
    f = open(filename, 'r')
    out = f.readlines()

    stored_data = []
    for line in out:
        if "#" not in line:
            print line
            stored_data.append(line)
    f.closed

    for i in range(len(stored_data)):
        g = open(stored_data[i], 'r')
        string = g.read()
        sth = json.loads(string)
        g.closed