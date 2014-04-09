#!/usr/bin/env python

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
            if "file_transfer" in data:

               f = file
               def dataReceived(self, data):
                   try:
                       try:
                           print format(json.loads(data))
                           print "got jason"
                           self.f=open("test.png","wb")

                           self.transport.write("ready")
                       except:
                           print "filedata incoming!"
                           self.f.write(data)
                   except:
                       print "unknown error" #happens if we don't receive json first

               def connectionLost(self, reason):
                   if self.f!=file:self.f.close()

                # filename = "files.txt"
                # f = open(filename, 'r')
                # out = f.readlines()
                #
                # stored_data = []
                # for line in out:
                #     if "#" not in line:
                #         print line
                #         stored_data.append(line)
                # f.closed
                #
                # for i in range(len(stored_data)):
                #     g = open(stored_data[i], 'r')
                #     string = g.read()
                #     sth = json.loads(string)
                #     print sth
                #     g.closed
                #     self.transport.write(str(sth))
            else:
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

