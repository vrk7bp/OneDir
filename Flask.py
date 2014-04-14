from flask import Flask, request, g, render_template, redirect, url_for, send_from_directory
from werkzeug import secure_filename 
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

dbName = "testUserDB"
tableName = "users"

DATABASE = 'testUserDB'

app = Flask(__name__)

#I think this needs to be changed to the individual user's folder
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

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
	
	new_id = request.headers['UserName']
	new_pass = request.headers['Password']

	users = access_user_table()

	if new_id in users:
		return "Username already in use!"
	else:
		cur = g.db.execute("INSERT INTO users (userName, password) VALUES (?, ?)", [new_id, new_pass])
		g.db.commit()
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
	return "This is the command recieved: " + command

#checks to see if the extension is allowed to be transferred 
def allowed_file(filename):
	return '.' in filename and \
	    filename.rsplit('.',1)[1] in app.config['ALLOWED_EXTENSIONS']

#uploads file
@app.route("/upload", methods = ['POST'])
def upload():
	#gets name of uploaded file
	file = request.files['file']
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		return redirect(url_for('uploaded_file', filename=filename))

#shows uploaded file on the browser after uploaded - not necessary but needed for upload function? 
@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
	


if __name__ == "__main__":
	app.run(debug=True)
