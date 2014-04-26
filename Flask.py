from flask import Flask
from flask import request
from flask import g
import sys
import time
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import fileinput
import json
import sqlite3
import shutil
from werkzeug.utils import secure_filename
import datetime

dbName = "testUserDB"
tableName = "users"

DATABASE = 'testUserDB'

UPLOAD_FOLDER = '/home/student/CS3240FinalProject/TestFolder'
USER_FOLDER = '/home/student/CS3240FinalProject/Users'
LOGS_FOLDER = '/home/student/CS3240FinalProject/Logs'
ACTIVITY_FOLDER = '/home/student/CS3240FinalProject/Statistics'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['USER_FOLDER'] = USER_FOLDER
app.config['LOGS_FOLDER'] = LOGS_FOLDER
app.config['ACTIVITY_FOLDER'] = ACTIVITY_FOLDER

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

##### WORKS ####
def connect_db():
	return sqlite3.connect(DATABASE)

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	if hasattr(g, 'db'):
		g.db.close()

def query_db(query, args=(), one=False):
	cur = g.db.execute(query, args)
	rv = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
	return (rv[0] if rv else None) if one else rv
#### WORKS ####

#Works...
@app.route('/addUser', methods = ['GET', 'POST'])
def handle_add_user_cmd():
    iden = check_login_id()
    new_id = request.headers['UserName']
    new_pass = request.headers['Password']

    users = access_user_table()

    if new_id in users:
        return "Username already in use!"
    else:
        if ("Admin" not in iden):
            if "Admin" in new_id:
                return "Not Allowed"
            else:
		        cur = g.db.execute("INSERT INTO users (userName, password) VALUES (?, ?)", [new_id, new_pass])
		        g.db.commit()
		        os.makedirs(USER_FOLDER + "/" + new_id)
		        os.open(LOGS_FOLDER + "/" + new_id, os.O_CREAT)
		        os.open(ACTIVITY_FOLDER + "/" + new_id, os.O_CREAT)
		        h = open("Statistics/" + new_id, 'w')
		        h.write("Total Files (including Folders): 0")
		        h.close()
		        return "Username Added"
        else:
            cur = g.db.execute("INSERT INTO users (userName, password) VALUES (?, ?)", [new_id, new_pass])
            g.db.commit()
            os.makedirs(USER_FOLDER + "/" + new_id)
            os.open(LOGS_FOLDER + "/" + new_id, os.O_CREAT)
            os.open(ACTIVITY_FOLDER + "/" + new_id, os.O_CREAT)
            h = open("Statistics/" + new_id, 'w')
            h.write("Total Files (including Folders): 0")
            h.close()
            return "Username Added"

#Works...
def access_user_table():
    try:
    	users = []
        cur = g.db.execute("select userName from " + tableName)
        rows = cur.fetchall()
        for row in rows:
            users.append(row[0]) #row[0] because the return type is a tuple
        return users

    except:
        return []

#Works...
@app.route("/check_login", methods = ['GET', 'POST'])
def check_if_one_login():
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
			return word[1]
		else:
			return ""
	except:
		return ""

#Works...
def check_login_status(): #We will go ahead and keep this log-in mechanism the same, just add a password check to the command handler.
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

#Works...
def check_login_id(): #We will go ahead and keep this log-in mechanism the same, just add a password check to the command handler.
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

@app.route("/", methods = ['GET', 'POST'])
def hello():
	return "Hello World!"

@app.route("/login", methods = ['GET', 'POST'])
def handle_login_cmd():
	users = access_user_table()
	id = request.headers['UserName']
	password = request.headers['Password']

	if id in users:
		if check_login_status():
			return "Logged in as: " + check_login_id()
		else:
			rightPassword = False
			cur = g.db.execute("select * from " + tableName + " where userName is \'" + id + "\';")
			rows = cur.fetchall()
			for row in rows:
				if(row[1] == password):
					rightPassword = True
			if rightPassword:
				w = open("login_info.txt", 'w')
				w.write("True " + id)
				w.close()
				return "Login Successful"
			else:
				return "Wrong Password"
	elif check_login_status():
		return "Logged in as: " + check_login_id()
	else:
		return "Invalid User"

@app.route("/change_pswd", methods = ['GET', 'POST'])
def handle_change_pass_cmd():
	users = access_user_table()
	id = request.headers['UserName']
	oldPass = request.headers['OldPass']
	newPass = request.headers['NewPass']

	if id in users:
		rightPassword = False
		cur = g.db.execute("select * from " + tableName + " where userName is \'" + id + "\';")
		rows = cur.fetchall()
		for row in rows:
			if(row[1] == oldPass):
				rightPassword = True
		if rightPassword:
			cur = g.db.execute("UPDATE users SET password=? WHERE userName=?;", [newPass, id])
			g.db.commit()
			return "Password Changed"
		else:
			return "Wrong Old Password"
	elif check_login_status():
		return "Error in the Program with changing password..."
	else:
		return "Error in the Program with changing password..."

@app.route("/admin_change_pswd", methods = ['GET', 'POST'])
def handle_admin_change_pass_cmd():
    users = access_user_table()
    adminID = request.headers['AdminID']
    adminPW = request.headers['AdminPW']
    userID = request.headers['UserName']
    userPW = request.headers['NewPass']

    if adminID in users:
        rightPassword = False
        cur = g.db.execute("select * from " + tableName + " where userName is \'" + adminID + "\';")
        rows = cur.fetchall()
        for row in rows:
            if (row[1] == adminPW):
                rightPassword = True
        if rightPassword:
            cur = g.db.execute("UPDATE users SET password=? WHERE userName=?;", [userPW, userID])
            g.db.commit()
            return "Password Changed"
        else:
            return "Wrong Admin Password"
    elif check_login_status():
        return "Error in the Program with changing password..."
    else:
        return "Error in the Program with changing password..."

@app.route("/admin_add_user", methods = ['GET', 'POST'])
def handle_admin_add_user_cmd():
	users = access_user_table()
	adminID = request.headers['AdminID']
	adminPW = request.headers['AdminPW']
	userID = request.headers['UserName']
	userPW = request.headers['NewPass']

	if adminID in users:
		rightPassword = False
		cur = g.db.execute("select * from " + tableName + " where userName is \'" + adminID + "\';")
		rows = cur.fetchall()
		for row in rows:
			if (row[1] == adminPW):
				rightPassword = True
		if rightPassword:
			iden = check_login_id()
			new_id = userID
			new_pass = userPW

			users = access_user_table()

			if new_id in users:
				return "Username already in use!"
			else:
				if ("Admin" not in iden):
					if "Admin" in new_id:
						return "Not Allowed"
					else:
						cur = g.db.execute("INSERT INTO users (userName, password) VALUES (?, ?)", [new_id, new_pass])
						g.db.commit()
						os.makedirs(USER_FOLDER + "/" + new_id)
						os.open(LOGS_FOLDER + "/" + new_id, os.O_CREAT)
						os.open(ACTIVITY_FOLDER + "/" + new_id, os.O_CREAT)
						h = open("Statistics/" + new_id, 'w')
						h.write("Total Files (including Folders): 0")
						h.close()
						return "Username Added"
				else:
					if "Admin" in new_id:
						cur = g.db.execute("INSERT INTO users (userName, password) VALUES (?, ?)", [new_id, new_pass])
						g.db.commit()
						os.makedirs(USER_FOLDER + "/" + new_id)
						os.open(LOGS_FOLDER + "/" + new_id, os.O_CREAT)
						os.open(ACTIVITY_FOLDER + "/" + new_id, os.O_CREAT)
						h = open("Statistics/" + new_id, 'w')
						h.write("Total Files (including Folders): 0")
						h.close()
						return "Username Added"
					else:
						cur = g.db.execute("INSERT INTO users (userName, password) VALUES (?, ?)", [new_id, new_pass])
						g.db.commit()
						os.makedirs(USER_FOLDER + "/" + new_id)
						os.open(LOGS_FOLDER + "/" + new_id, os.O_CREAT)
						os.open(ACTIVITY_FOLDER + "/" + new_id, os.O_CREAT)
						h = open("Statistics/" + new_id, 'w')
						h.write("Total Files (including Folders): 0")
						h.close()
						return "Username Added"
		else:
			return "Wrong Admin Password"
	elif check_login_status():
		return "Error in the Program with adding a new user.."
	else:
		return "Error in the Program with adding a new user..."

@app.route("/admin_delete_user", methods = ['GET', 'POST'])
def handle_admin_delete_user_cmd():
    users = access_user_table()
    adminID = request.headers['AdminID']
    adminPW = request.headers['AdminPW']
    userID = request.headers['UserName']
    filesToo = request.headers['FilesToo']

    if adminID in users:
        rightPassword = False
        cur = g.db.execute("select * from " + tableName + " where userName is \'" + adminID + "\';")
        rows = cur.fetchall()
        for row in rows:
            if (row[1] == adminPW):
                rightPassword = True
        if rightPassword:
            cur = g.db.execute("DELETE from users WHERE userName=?", [userID])
            g.db.commit()
            if(filesToo == "True"):
            	shutil.rmtree(USER_FOLDER + "/" + userID)
            	os.remove(LOGS_FOLDER + "/" + userID)
            	os.remove(ACTIVITY_FOLDER + "/" + userID)
            return "User <" + userID + "> Deleted"
        else:
            return "Wrong Admin Password"
    elif check_login_status():
        return "Error in the Program with changing password..."
    else:
        return "Error in the Program with changing password..."


@app.route("/alt_login", methods = ['GET', 'POST'])
def handle_alt_login():
	id = request.headers['UserName']
	password = request.headers['Password']
	currentUser = check_login_id()

	if id == currentUser:
		rightPassword = False
		cur = g.db.execute("select * from " + tableName + " where userName is \'" + id + "\';")
		rows = cur.fetchall()
		for row in rows:
			if(row[1] == password):
				rightPassword = True
		if rightPassword == False:
			return "Wrong Password"
		return "Login Successful"
	elif check_login_status():
		return "Bad UserName"
	else:
		return "Invalid User"

@app.route("/logout", methods = ['GET', 'POST'])
def handle_logout():
	w = open("login_info.txt", 'w')
	w.write("False " + "None")
	w.close()
	return "Logged Out"
#### WORKS ####

@app.route("/command", methods = ['GET', 'POST'])
def handle_command():
	command = request.headers['Value']
	index = command.find(":")
	login = check_login_id()

	w = open("Logs/" + login, 'a')
	w.write(command + " (at " + str(datetime.datetime.now()) + ")" "\n")
	w.close()

	content = []
	with open("Statistics/TotalStats") as f:
		content = f.readlines()
	for elements in content:
		colon = elements.find(":")
		intVal = int(elements[colon+2:])
		if command[0:index] == "Delete" or command[0:index] == "DirDelete":
			intVal = intVal -1
		elif command[0:index] == "Transfer" or command[0:index] == "DirCreate":
			intVal += 1
		h = open("Statistics/TotalStats", 'w')
		h.write("Total Files (including Folders): " + str(intVal))
		h.close()

	with open("Statistics/" + login) as f:
		content = f.readlines()
	for elements in content:
		colon = elements.find(":")
		intVal = int(elements[colon+2:])
		if command[0:index] == "Delete" or command[0:index] == "DirDelete":
			intVal = intVal - 1
		elif command[0:index] == "Transfer" or command[0:index] == "DirCreate":
			intVal += 1
		h = open("Statistics/" + login, 'w')
		h.write("Total Files (including Folders): " + str(intVal))
		h.close()

	return "This is the command recieved: " + command

#### Dealing with File Transfer Here ####

@app.route('/file_transfer', methods=['GET', 'POST'])
def upload_file():
	file = request.files['file']
	command = request.headers['command']
	thePath = command[40:]
	login = check_login_id()
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		return  "File uploaded correctly"
	return command


if __name__ == "__main__":
	app.run(debug=True)