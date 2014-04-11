#!/usr/bin/env python

from twisted.internet import protocol, reactor
from time import ctime, time
import os
import fileinput
import json
import sqlite3

PORT = 21567

allowed_users = ["tom", "ali"]

dbName = "testUserDB"
tableName = "users"

class TSServProtocol(protocol.Protocol):
    def connectionMade(self):
        clnt = self.clnt = self.transport.getPeer().host
        print '...connected from:', clnt

    def dataReceived(self, in_msg):
        self.process_incoming(in_msg)

    def access_user_table(self):
        try:
            connection = sqlite3.connect(dbName)
            cursor = connection.cursor()
            cursor.execute("select userName from " + tableName)
            users = []

            rows = cursor.fetchall()
            for row in rows:
                users.append(row[0]) #row[0] because the return type is a tuple

            connection.close()

            return users

        except:
            return []

    def check_login_status(self): #We will go ahead and keep this log-in mechanism the same, just add a password check to the command handler.
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

    def check_login_id(self): #We will go ahead and keep this log-in mechanism the same, just add a password check to the command handler.
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

        users = self.access_user_table()

        id = msg_data["user_id"]
        password = msg_data["password"]
        if id in users:
            if self.check_login_status():
                self.transport.write("Logged in as: " + self.check_login_id())
            else:
                rightPassword = False
                connection = sqlite3.connect(dbName)
                cursor = connection.cursor()
                cursor.execute("select * from " + tableName + " where userName is \'" + id + "\';")
                rows = cursor.fetchall()
                for row in rows:
                    if(row[1] == password):
                        rightPassword = True
                connection.close()
                if rightPassword:
                    w = open("login_info.txt", 'w')
                    w.write("True " + id)
                    w.close()
                    self.transport.write(" Login Successful")
                else:
                    self.transport.write(" Wrong Password")
        elif self.check_login_status():
            self.transport.write("Logged in as: " + self.check_login_id())
        else:
            self.transport.write("Invalid User")

    def handle_logout_cmd(self, msg_data):
        w = open("login_info.txt", 'w')
        w.write("False " + "None")
        w.close()
        self.transport.write("Logged Out")

    def handle_add_user_cmd(self, msg_data):
        self.transport.write("Adding user...")

        users = self.access_user_table()

        new_id = msg_data["user_id"]
        new_pass = msg_data["password"]
        if new_id in users:
            self.transport.write(" Username already in use!")
        else:
            connection = sqlite3.connect(dbName)
            cursor = connection.cursor()
            execute = "INSERT INTO %s (userName, password) VALUES(\'%s\', \'%s\')" % (tableName, new_id, new_pass)
            cursor.execute(execute)
            connection.commit()
            connection.close()

    def handle_delete_myself_cmd(self, msg_data):
        self.transport.write(self.check_login_id() + " removed from users")
        userName = self.check_login_id()
        connection = sqlite3.connect(dbName)
        cursor = connection.cursor()
        execute = "DELETE FROM %s where userName = \'%s\'" % (tableName, userName)
        cursor.execute(execute)
        connection.commit()
        connection.close()
        self.handle_logout_cmd(msg_data)

    def handle_file_transfer_cmd(self, msg_data):
        self.transport.write("Transferring file")

    def handle_user_cmd(self, msg_data):
        self.transport.write("response for 'user' cmd")

    def handle_write_cmd(self, msg_data):
        self.transport.write("response for 'write' cmd")

    def handle_invalid_cmd(self, msg_data):
        self.transport.write("response for 'invalid' cmd")

    def process_incoming(self, json_msg):
        try:
            msg_data = json.loads(json_msg)
            cmd = msg_data["cmd"]
        except ValueError:
            cmd = None
        print "Server processing: ", cmd

        if self.check_login_status():
            if cmd == "user":
                self.handle_user_cmd(msg_data)
            elif cmd == "write":
                self.handle_write_cmd(msg_data)
            elif cmd == "delete_myself": #Works fine with SQLite3
                self.handle_delete_myself_cmd(msg_data)
            elif cmd == "add_user":
                self.handle_add_user_cmd(msg_data)
            elif cmd == "file_transfer":
                self.handle_file_transfer_cmd(msg_data)
            elif cmd == "login": #Works fine with SQLite3
                self.transport.write("Logged in as: " + self.check_login_id())
            elif cmd == "logout": #Works fine with SQLite3
                self.handle_logout_cmd(msg_data)
            else:
                self.handle_invalid_cmd(json_msg)
        elif (cmd == "user") or (cmd == "write") or (cmd == "delete_myself") or (cmd == "file_transfer") or (cmd == "logout"):
            self.transport.write("You must be logged in for that command")
        elif cmd == "login":
            self.handle_login_cmd(msg_data) #Login requires cmd, user_id, password (works with SQLite3)
        elif cmd == "add_user":
            self.handle_add_user_cmd(msg_data) #Add user requires cmd, user_id, password (works with SQLite3)
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

if __name__ == "__main__":
    factory = protocol.Factory()
    factory.protocol = TSServProtocol
    print 'waiting for connection on PORT: ', PORT
    reactor.listenTCP(PORT, factory)
    reactor.run()

