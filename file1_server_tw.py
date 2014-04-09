#!/usr/bin/env python


"""
TCP file server using Twisted.  The goal of this simple demo was to show:
a) How a JSON string can be used to send complex data (lists, dictionaries)
b) How this could be used to send commands and data to go with those commands
c) how the server could be made recognize commands and be structured to handle them.

(NOTE: This is just a demo.  It's not necessarily a great design. It's to show how
something might be done.)

3rd party libraries need to be installed to run this!  Use pip to install:
a) Twisted

How to run these.  (Might be easier to run these from the command-line.)
a) Start the server, this program.
b) Start the client, file1_client_tw.py, on the same computer. (In a different window.)
c) In the client, type a Python dictionary, where one key is "cmd" -- this could be
the "command" you're sending.  The server recognizes these commands: user, write, delete.
A method is called for each one of these, and right now the server just sends
back an acknowledgment and ignores other data in the dictionary.  But you can see how this
could be the start of implementing a protocol.
Example of valid input:  {"cmd" : "user", "user_id" : "horton"}
d) Hit return in the client to stop the client.
e) In the server window, Hit CTRL-C or whatever your operating system requires to kill a running program.

It should be possible to run these on two different computers.
Start the server on one machine.
When you start the client on the 2nd machine, give a command-line argument: the IP address
or full internet hostname of the server machine.

"""

from twisted.internet import protocol, reactor
from time import ctime, time
import os
import fileinput
import json

PORT = 21567

allowed_users = ["tom", "ali"]

class TSServProtocol(protocol.Protocol):
    def connectionMade(self):
        clnt = self.clnt = self.transport.getPeer().host
        print '...connected from:', clnt

    def dataReceived(self, in_msg):
        self.process_incoming(in_msg)
        # out_msg = '[%s] %s' % (ctime(), in_msg)
        # self.transport.write(out_msg)

    def check_login_status(self, msg_data):
        try:
            r = open("login_info.txt", 'r')
            out = r.readlines()
            info = []
            for i in out:
                word = i.split(" ")
                for j in range(len(word)):
                    if word != " ":
                        info.append(word[j])
            r.closed

            if word[0] == "True":
                return True
            else:
                return False
        except:
            return False

    def check_login_id(self, msg_data):
        try:
            r = open("login_info.txt", 'r')
            out = r.readlines()
            info = []
            for i in out:
                word = i.split(" ")
                for j in range(len(word)):
                    if word != " ":
                        info.append(word[j])
            r.closed

            return word[1]
        except:
            return ""

    def handle_login_cmd(self, msg_data):
        self.transport.write("logging in...")
        try:
            r = open("user_list.txt", 'r')
            out = r.readlines()
            users = []

            for i in out:
                word = i.split(" ")
                for j in range(len(word)):
                    if word != " ":
                        users.append(word[j])
            r.closed

            id = msg_data["user_id"]
            if id in users:
                if self.check_login_status(msg_data):
                    self.transport.write("Logged in as: " + self.check_login_id(msg_data))
                else:
                    w = open("login_info.txt", 'w')
                    w.write("True " + id)
                    w.close()
                    self.transport.write("Login Successful")
            else:
                self.transport.write("Invalid User")
        except:
            self.transport.write("Invalid User")

    def handle_logout_cmd(self, msg_data):
        w = open("login_info.txt", 'w')
        w.write("False " + "None")
        w.close()
        self.transport.write("Logged Out")

    def handle_add_user_cmd(self, msg_data):
        self.transport.write("Adding user...")
        try:
            r = open("user_list.txt", 'r')
            out = r.readlines()
            users = []

            for i in out:
                word = i.split(" ")
                for j in range(len(word)):
                    if word != " ":
                        users.append(word[j])
            r.closed

            new_id = msg_data["user_id"]
            if new_id in users:
                self.transport.write("Username already in use!")
            else:
                w = open("user_list.txt", 'w')
                for i in range(len(users)):
                    w.write(users[i])
                    w.write(" ")
                w.write(new_id)
                w.close()
        except:
            w = open("user_list.txt", 'w')
            w.write(msg_data["user_id"])
            w.write(" ")
            w.close()

    def handle_file_transfer_cmd(self, msg_data):
        self.transport.write("Transferring file")

    def handle_user_cmd(self, msg_data):
        self.transport.write("response for 'user' cmd")
        print msg_data["user_id"]

    def handle_write_cmd(self, msg_data):
        self.transport.write("response for 'write' cmd")

    def handle_delete_cmd(self, msg_data):
        self.transport.write("response for 'delete' cmd")

    def handle_invalid_cmd(self, msg_data):
        self.transport.write("response for 'invalid' cmd")


    def process_incoming(self, json_msg):
        try:
            msg_data = json.loads(json_msg)
            cmd = msg_data["cmd"]
        except ValueError:
            cmd = None
        print "Server processing: ", cmd

        if self.check_login_status(msg_data):
            if cmd == "user":
                self.handle_user_cmd(msg_data)
            elif cmd == "write":
                self.handle_write_cmd(msg_data)
            elif cmd == "delete":
                self.handle_delete_cmd(msg_data)
            elif cmd == "add_user":
                self.handle_add_user_cmd(msg_data)
            elif cmd == "file_transfer":
                self.handle_file_transfer_cmd(msg_data)
            elif cmd == "login":
                self.handle_login_cmd(msg_data)
            elif cmd == "logout":
                self.handle_logout_cmd(msg_data)
            else:
                self.handle_invalid_cmd(json_msg)
        elif cmd == "login":
            self.handle_login_cmd(msg_data)
        elif cmd == "add_user":
            self.handle_add_user_cmd(msg_data)
        else:
            self.transport.write("Invalid User")

    def test_process_incoming1(self):
        self.process_incoming('{"cmd" : "user", "user_id" : "horton"}')


def store_data(user, filename, data):
    path = os.path.join(os.getcwd(), user)
    if not os.path.exists(path):
        os.mkdir(path)
    with open( os.path.join(path, filename), "w") as f:
        f.write(data)
    print "server wrote data to: ", os.path.join(path, filename)


# def test_store_data1():
#     store_data("user1", "foo.txt", "here's some data stored at "+ str(time()))

if __name__ == "__main__":
    # test_process_incoming1()
    factory = protocol.Factory()
    factory.protocol = TSServProtocol
    print 'waiting for connection on PORT: ', PORT
    reactor.listenTCP(PORT, factory)
    reactor.run()

