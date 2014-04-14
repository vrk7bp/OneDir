import WatchDogWithClient
import sys
import time
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from twisted.internet import protocol, reactor
import sys
import fileinput
import json

HOST = '127.0.0.1'
PORT = 21567

if __name__ == "__main__":
	StringUserName = None;
	StringPassword = None;
	while(True):
		print "Welcome to OneDirection..."
		UserName = raw_input("Please put in your UserName: ")

		try:
			StringUserName = str(UserName)
			break
		except:
			print "That was not a valid input for the UserName..."

	while(True):
		Password = raw_input("Please put in your Password: ")
		try:
			StringPassword = str(Password)
			break
		except:
			print "That was not a valid input for the Password..."

	if len(sys.argv) > 1:
		HOST = sys.argv[1]

	print "Connecting to (HOST, PORT): ", (HOST, PORT)

	reactor.connectTCP(HOST, PORT, WatchDogWithClient.TSClntFactory())
	reactor.run()

	while(True):
		print "Trying to log-in..."
		data = "{\"cmd\": \"login\", \"user_id\": \"" + StringUserName + "\", \"password\": \"" + StringPassword + "\"}"
		print data
		testing = WatchDogWithClient.TSClntProtocol()
		testing.transport.write(data)
		break