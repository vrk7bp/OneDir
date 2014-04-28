from flask import request, redirect, Flask, g, url_for, send_from_directory
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
tableNameU = "users"
tableNameDU = "deleted_users"

DATABASE = 'testUserDB'

UPLOAD_FOLDER = '/home/ubuntu/CS3240FinalProject/TestFolder'
USER_FOLDER = '/home/ubuntu/CS3240FinalProject/Users'
LOGS_FOLDER = '/home/ubuntu/CS3240FinalProject/Logs'
ACTIVITY_FOLDER = '/home/ubuntu/CS3240FinalProject/Statistics'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py'])

AmountOfUsers = 0

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

#Works...
def access_user_table():
    try:
    	users = []
        cur = g.db.execute("select userName from " + tableNameU)
        rows = cur.fetchall()
        for row in rows:
            users.append(row[0]) #row[0] because the return type is a tuple
        return users

    except:
        return []
#Works...
def access_deleted_user_table():
    try:
    	users = []
        cur = g.db.execute("select user from " + tableNameDU)
        rows = cur.fetchall()
        for row in rows:
            users.append(row[0]) #row[0] because the return type is a tuple
        return users

    except:
        return []

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

def log_act(user, act):
    print "?"
    cur = g.db.execute("CREATE TABLE IF NOT EXISTS activity_log(userName text, activity text, time TIMESTAMP WITH LOCAL TIME ZONE)")
    cur = g.db.execute("INSERT INTO activity_log(userName, activity, time) VALUES (?, ?, datetime(CURRENT_TIMESTAMP, 'localtime') )", [user, act])
    g.db.commit()
    return 0

def makeListOfAccountLogIns():
	if AmountOfUsers == 0:
		open("../AccountNumbers.txt", 'w').close()
	else:
		open("../AccountNumbers.txt", 'w').close()
		f = open("../AccountNumbers.txt", 'w')
		for elements in range(1, AmountOfUsers+1):
			stringNum = str(elements)
			f.write(stringNum + "\n")
		f.close()

def takeNumberOut(number):
	listOfNums = [int(line.strip()) for line in open('../AccountNumbers.txt')]
	for element in range(len(listOfNumbs)):
		print str(element)
	# f = open("../AccountNumbers.txt", 'r')
	# out = f.readlines()
	# for i in out:
	# 	listOfNums.append(int(i.strip()))
	# f.close()

	listOfNums.remove(number)

	open("../AccountNumbers.txt", 'w').close()
	a = open("../AccountNumbers.txt", 'w')
	for elements in range(len(listOfNums)):
		stringNum = str(listOfNums[elements])
		a.write(stringNum + "\n")
	a.close()

def checkIfNumberIsIn(number):
	listOfNums = [int(line.strip()) for line in open('../AccountNumbers.txt')]
	# f = open("../AccountNumbers.txt", 'r')
	# out = f.readlines()
	# for i in out:
	# 	listOfNums.append(int(i.strip()))
	# f.close()

	if listOfNums.count(number) == 0:
		return False
	return True

def clearOperationsFile():
	open("../OperationsToUpdate.txt", 'w').close()

def getOperationsAsString():
	with open("../OperationsToUpdate.txt") as f:
		content = f.readlines()
	returnString = ""
	for elements in content:
		returnString += elements
	return returnString

@app.route("/get_update", methods = ['GET', 'POST'])
def get_update():
	number = request.headers['Number']
	if(checkIfNumberIsIn(int(number))):
		takeNumberOut(int(number))
		return getOperationsAsString()
	else:
		return "Up to Date"

@app.route("/get_the_file", methods = ['GET', 'POST'])
def get_the_file():
	path = request.headers['Path']
	login = check_login_id()

	return send_from_directory(app.config['USER_FOLDER'] + "/" + login, path)


@app.route("/", methods = ['GET', 'POST'])
def hello():
	return "Hello World!"

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

@app.route("/login", methods = ['GET', 'POST'])
def handle_login_cmd():
	global AmountOfUsers
	users = access_user_table()
	id = request.headers['UserName']
	password = request.headers['Password']

	if id in users:
		if check_login_status():
			return "Logged in as: " + check_login_id()
		else:
			rightPassword = False
			cur = g.db.execute("select * from " + tableNameU + " where userName is \'" + id + "\';")
			rows = cur.fetchall()
			for row in rows:
				if(row[1] == password):
					rightPassword = True
			if rightPassword:
				w = open("login_info.txt", 'w')
				w.write("True " + id)
				w.close()
				log_act(id, "Logged in")
				AmountOfUsers += 1
				return "Login Successful (" + str(AmountOfUsers) + ")"
			else:
				return "Wrong Password"
	elif check_login_status():
		return "Logged in as: " + check_login_id()
	else:
		return "Invalid User"

@app.route("/alt_login", methods = ['GET', 'POST'])
def handle_alt_login():
	global AmountOfUsers
	id = request.headers['UserName']
	password = request.headers['Password']
	currentUser = check_login_id()

	if id == currentUser:
		rightPassword = False
		cur = g.db.execute("select * from " + tableNameU + " where userName is \'" + id + "\';")
		rows = cur.fetchall()
		for row in rows:
			if(row[1] == password):
				rightPassword = True
		if rightPassword == False:
			return "Wrong Password"
		log_act(currentUser, "Logged in from another computer")
		AmountOfUsers += 1
		return "Login Successful (" + str(AmountOfUsers) + ")"
	elif check_login_status():
		return "Bad UserName"
	else:
		return "Invalid User"

#Works...
@app.route('/addUser', methods = ['GET', 'POST'])
def handle_add_user_cmd():
	commandingUser = check_login_id()
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
				log_act(new_id, "created own account")
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
			log_act(new_id, "created own account")
			return "Username Added"

@app.route("/change_pswd", methods = ['GET', 'POST'])
def handle_change_pass_cmd():
    commandingUser = check_login_id()
    users = access_user_table()
    id = request.headers['UserName']
    oldPass = request.headers['OldPass']
    newPass = request.headers['NewPass']

    if id in users:
        rightPassword = False
        cur = g.db.execute("select * from " + tableNameU + " where userName is \'" + id + "\';")
        rows = cur.fetchall()
        for row in rows:
            if (row[1] == oldPass):
                rightPassword = True
        if rightPassword:
            cur = g.db.execute("UPDATE users SET password=? WHERE userName=?;", [newPass, id])
            g.db.commit()
            log_act(commandingUser, "changed own Password")
            return "Password Changed"
        else:
            return "Wrong Old Password"
    elif check_login_status():
        return "Error in the Program with changing password..."
    else:
        return "Error in the Program with changing password..."

@app.route("/admin_change_pswd", methods = ['GET', 'POST'])
def handle_admin_change_pass_cmd():
    commandingUser = check_login_id()
    users = access_user_table()
    adminID = request.headers['AdminID']
    adminPW = request.headers['AdminPW']
    userID = request.headers['UserName']
    userPW = request.headers['NewPass']

    if adminID in users:
        rightPassword = False
        cur = g.db.execute("select * from " + tableNameU + " where userName is \'" + adminID + "\';")
        rows = cur.fetchall()
        for row in rows:
            if (row[1] == adminPW):
                rightPassword = True
        if rightPassword:
            cur = g.db.execute("UPDATE users SET password=? WHERE userName=?;", [userPW, userID])
            g.db.commit()
            log_act(commandingUser, "changePassword for " + userID)
            return "Password Changed"
        else:
            return "Wrong Admin Password"
    elif check_login_status():
        return "Error in the Program with changing password..."
    else:
        return "Error in the Program with changing password..."

@app.route("/admin_add_user", methods = ['GET', 'POST'])
def handle_admin_add_user_cmd():
	commandingUser = check_login_id()
	users = access_user_table()
	adminID = request.headers['AdminID']
	adminPW = request.headers['AdminPW']
	userID = request.headers['UserName']
	userPW = request.headers['NewPass']

	if adminID in users:
		rightPassword = False
		cur = g.db.execute("select * from " + tableNameU + " where userName is \'" + adminID + "\';")
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
						log_act(commandingUser, "createdUser " + new_id)
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
						log_act(commandingUser, "createdUser " + new_id)
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
						log_act(commandingUser, "createdUser " + new_id)
						return "Username Added"
		else:
			return "Wrong Admin Password"
	elif check_login_status():
		return "Error in the Program with adding a new user.."
	else:
		return "Error in the Program with adding a new user..."

@app.route("/admin_delete_user", methods = ['GET', 'POST'])
def handle_admin_delete_user_cmd():
    commandingUser = check_login_id()
    users = access_user_table()
    adminID = request.headers['AdminID']
    adminPW = request.headers['AdminPW']
    userID = request.headers['UserName']
    filesToo = request.headers['FilesToo']

    deletedUsers = access_deleted_user_table()

    if adminID in users:
        rightPassword = False
        cur = g.db.execute("select * from " + tableNameU + " where userName is \'" + adminID + "\';")
        rows = cur.fetchall()
        for row in rows:
            if (row[1] == adminPW):
                rightPassword = True
        if rightPassword:
            cur = g.db.execute("DELETE from users WHERE userName=?", [userID])
            g.db.commit()
            cur = g.db.execute("CREATE TABLE IF NOT EXISTS deleted_users(user text)")
            g.db.commit()
            if userID not in deletedUsers:
                cur = g.db.execute("INSERT INTO deleted_users(user) VALUES (?)", [userID])
            g.db.commit()
            log_act(commandingUser, userID + " Deleted")
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

@app.route("/logout", methods = ['GET', 'POST'])
def handle_logout():
	global AmountOfUsers
	commandingUser = check_login_id()
	log_act(commandingUser, "Logged Out")
	w = open("login_info.txt", 'w')
	w.write("False " + "None")
	w.close()
	AmountOfUsers = 0
	return "Logged Out"

@app.route("/admin_get_user_info", methods = ['GET', 'POST'])
def get_user_info():
	commandingUser = check_login_id()
	users = access_user_table()
	adminID = request.headers['AdminID']
	adminPW = request.headers['AdminPW']
	userID = request.headers['UserName']

	if adminID in users:
		rightPassword = False
		cur = g.db.execute("select * from " + tableNameU + " where userName is \'" + adminID + "\';")
		rows = cur.fetchall()
		for row in rows:
			if (row[1] == adminPW):
				rightPassword = True
		if rightPassword:
			if userID in users:
				newCur = g.db.execute("select * from " + tableNameU + " where userName is \'" + userID + "\';")
				rows = newCur.fetchall()
				log_act(commandingUser, "Got info for " + userID)
				for row in rows:
					return row[1]
			else:
				return "That UserName doesn't exist."
		else:
			return "Wrong Admin Password"
	elif check_login_status():
		return "Error in the Program with getting user info..."
	else:
		return "Error in the Program with getting user info..."

@app.route("/admin_get_stats", methods = ['GET', 'POST'])
def get_admin_stats():
	commandingUser = check_login_id()
	users = access_user_table()
	adminID = request.headers['AdminID']
	adminPW = request.headers['AdminPW']
	userID = request.headers['UserName']

	if adminID in users:
		rightPassword = False
		cur = g.db.execute("select * from " + tableNameU + " where userName is \'" + adminID + "\';")
		rows = cur.fetchall()
		for row in rows:
			if (row[1] == adminPW):
				rightPassword = True
		if rightPassword:
			if userID == "total":
				with open("Statistics/TotalStats") as f:
					content = f.readlines()
				log_act(commandingUser, "Got total statistics")
				for elements in content:
					return elements
			else:
				if userID in users:
					with open("Statistics/" + userID) as f:
						content = f.readlines()
					log_act(commandingUser, "Got statistics for " + userID)
					for elements in content:
						return elements
				else:
					return "That UserName doesn't exist."
		else:
			return "Wrong Admin Password"
	elif check_login_status():
		return "Error in the Program with getting user stats..."
	else:
		return "Error in the Program with getting user stats..."

@app.route("/admin_user_deletes", methods = ['GET', 'POST'])
def get_admin_deletes():
	commandingUser = check_login_id()
	users = access_user_table()
	adminID = request.headers['AdminID']
	adminPW = request.headers['AdminPW']

	if adminID in users:
		rightPassword = False
		cur = g.db.execute("select * from " + tableNameU + " where userName is \'" + adminID + "\';")
		rows = cur.fetchall()
		for row in rows:
			if (row[1] == adminPW):
				rightPassword = True
		if rightPassword:
			newCur = g.db.execute("select * from " + tableNameDU + ";")
			theList = newCur.fetchall()
			log_act(commandingUser, "Got list of deleted users")
			stringReturn = ""
			for row in theList:
				stringReturn += row[0] + "\n"
			return stringReturn
		else:
			return "Wrong Admin Password"
	elif check_login_status():
		return "Error in the Program with getting user deletes..."
	else:
		return "Error in the Program with getting user deletes..."

@app.route("/admin_get_user_operations", methods = ['GET', 'POST'])
def get_admin_operations():
	commandingUser = check_login_id()
	users = access_user_table()
	adminID = request.headers['AdminID']
	adminPW = request.headers['AdminPW']
	userID = request.headers['UserName']
	totalOPs = request.headers['OpsTotal']

	if adminID in users:
		rightPassword = False
		cur = g.db.execute("select * from " + tableNameU + " where userName is \'" + adminID + "\';")
		rows = cur.fetchall()
		for row in rows:
			if (row[1] == adminPW):
				rightPassword = True
		if rightPassword:
			if totalOPs == "total":
				newCur = g.db.execute("select * from activity_log;")
				theList = newCur.fetchall()
				stringReturn = ""
				log_act(commandingUser, "Got total user operations")
				for row in theList:
					stringReturn += "UserName: " + row[0] + ", Operation: " + row[1] + ", Time: " + str(row[2]) + "\n"
				return stringReturn
			else:
				if userID in users:
					newCur = g.db.execute("select * from activity_log where userName is \'" + userID + "\';")
					theList = newCur.fetchall()
					stringReturn = ""
					log_act(commandingUser, "Got user operations for " + userID)
					for row in theList:
						stringReturn += "UserName: " + row[0] + ", Operation: " + row[1] + ", Time: " + str(row[2]) + "\n"
					return stringReturn
				else:
					return "That UserName doesn't exist."
		else:
			return "Wrong Admin Password"
	elif check_login_status():
		return "Error in the Program with getting user info..."
	else:
		return "Error in the Program with getting user info..."

@app.route("/admin_get_user_logs", methods = ['GET', 'POST'])
def get_admin_logs():
	commandingUser = check_login_id()
	users = access_user_table()
	adminID = request.headers['AdminID']
	adminPW = request.headers['AdminPW']
	userID = request.headers['UserName']

	if adminID in users:
		rightPassword = False
		cur = g.db.execute("select * from " + tableNameU + " where userName is \'" + adminID + "\';")
		rows = cur.fetchall()
		for row in rows:
			if (row[1] == adminPW):
				rightPassword = True
		if rightPassword:
			if userID in users:
				with open("Logs/" + userID) as f:
					content = f.readlines()
				log_act(commandingUser, "Got logs for " + userID)
				returnString = ""
				for elements in content:
					returnString += elements
				return returnString
			else:
				return "That UserName doesn't exist."
		else:
			return "Wrong Admin Password"
	elif check_login_status():
		return "Error in the Program with getting user info..."
	else:
		return "Error in the Program with getting user info..."

@app.route("/command", methods = ['GET', 'POST'])
def handle_command():
	commandingUser = check_login_id()
	command = request.headers['Value']
	index = command.find(":")
	login = check_login_id()
	try:
		theFile = request.files['file']
	except:
		theFile = {}

	makeListOfAccountLogIns()

	w = open("Logs/" + login, 'a')
	w.write(command + " (at " + str(datetime.datetime.now()) + ")" + "\n")
	w.close()

	q = open("../OperationsToUpdate.txt", 'a')
	q.write(command + "\n")
	q.close()
	#log_act(commandingUser, command)

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

	if command[0:index] == "Move":
		dic = {'Value': command[index+4:]}
		return redirect(url_for('moving_file', headers=dic), code=307)
	elif command[0:index] == "Transfer":
		dic = {'Value': command[index+4:]}
		newFile = {'file': theFile}
		return redirect(url_for('upload_file', files=newFile, headers=dic), code=307)
	elif command[0:index] == "Delete":
		dic = {'Value': command[index+4:]}
		return redirect(url_for('delete_file', headers=dic), code=307)
	elif command[0:index] == "DirCreate":
		dic = {'Value': command[index+4:]}
		return redirect(url_for('create_direc', headers=dic), code=307)
	elif command[0:index] == "DirDelete":
		dic = {'Value': command[index+4:]}
		return redirect(url_for('delete_direc', headers=dic), code=307)
	elif command[0:index] == "DirMove":
		dic = {'Value': command[index+4:]}
		return redirect(url_for('moving_direc', headers=dic), code=307)

	return "This is the command recieved: " + command

@app.route('/create_direc', methods=['GET', 'POST'])
def create_direc():
	interVal = request.headers['Value']
	index = interVal.find(":")
	Directory = interVal[index+3:]
	login = check_login_id()
	os.makedirs(USER_FOLDER + "/" + login + "/" + Directory)
	return "Directory Creation"

@app.route('/delete_direc', methods=['GET', 'POST'])
def delete_direc():
	interVal = request.headers['Value']
	index = interVal.find(":")
	Directory = interVal[index+3:]
	login = check_login_id()
	shutil.rmtree(USER_FOLDER + "/" + login + "/" + Directory)
	return "Directory Deletion"

@app.route('/move_direc', methods=['GET', 'POST'])
def moving_direc():
	#Directory
	interVal = request.headers['Value']
	index = interVal.find(":")
	login = check_login_id()
	Directory = str(interVal[index+3:])

	#Source
	toIndex = Directory.find(":")
	sourceTemp = Directory[0:toIndex-1]
	indexSlashSource = sourceTemp.rfind("/")
	source = "Users/" + login + "/" + sourceTemp

	#dest
	destTemp = Directory[toIndex+5:]
	indexSlash = destTemp.rfind("/")
	dest = "Users/" + login + destTemp

	shutil.move(source, dest)
	return "Directory Move"

@app.route('/delete_file', methods=['GET', 'POST'])
def delete_file():
	interVal = request.headers['Value']
	index = interVal.find(":")
	Directory = interVal[index+3:]
	login = check_login_id()
	os.remove(USER_FOLDER + "/" + login + "/" + Directory)
	return "File Deletion"

@app.route('/move_file', methods=['GET', 'POST'])
def moving_file():
	#Directory
	interVal = request.headers['Value']
	index = interVal.find(":")
	login = check_login_id()
	Directory = str(interVal[index+3:])

	#Source
	toIndex = Directory.find(":", index+1)
	sourceTemp = Directory[0:toIndex-1]
	indexSlashSource = sourceTemp.rfind("/")
	source = "Users/" + login + "/" + sourceTemp

	#dest
	destTemp = Directory[toIndex+5:]
	indexSlash = destTemp.rfind("/")
	dest = "Users/" + login + destTemp
	shutil.move(source, dest)
	return "File Move"

@app.route('/file_transfer', methods=['GET', 'POST'])
def upload_file():
	fileName = request.files['file']
	interVal = request.headers['Value']
	index = interVal.find(":")
	Directory = interVal[index+3:]
	login = check_login_id()
	if fileName and allowed_file(fileName.filename):
		filename = secure_filename(fileName.filename)
		os.open(os.path.join(app.config['USER_FOLDER'], login, Directory), os.O_CREAT)
		fileName.save(os.path.join(app.config['USER_FOLDER'], login, Directory))
		return  "File uploaded correctly"
	return Directory

if __name__ == "__main__":
	app.run('0.0.0.0', 8080, debug=True)
