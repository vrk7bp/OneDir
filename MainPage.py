import sys
import time
import os
import threading
from multiprocessing import Process, Value, Array
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import fileinput
import json
import sqlite3

#HOST = "http://127.0.0.1:5000"

HOST = "http://54.84.161.128:8080"

#HOST = "http://ec2-54-86-100-75.compute-1.amazonaws.com:5000"

LOGIN_URL = HOST + "/login"
ADD_USER_URL = HOST +"/addUser"
TEST = HOST + "/testing"
CHECK_USER = HOST + "/check_login"
ALT_LOGIN = HOST + "/alt_login"
LOGOUT = HOST + "/logout"
CHANGE_PASS = HOST + "/change_pswd"
COMMAND = HOST + "/command"

## Shouldn't ever have to really use these...
FILE_TRANSFER = HOST + "/file_transfer"
CREATE_DIREC = HOST + "/create_direc"
DELETE_DIREC = HOST + "/delete_direc"
MOVE_DIREC = HOST + "/move_direc"
DELETE_FILE = HOST + "/delete_file"
MOVE_FILE = HOST + "/move_file"
GET_FILE = HOST + "/get_the_file"
GET_UPDATE = HOST + "/get_update"
## End

ADMIN_CHANGE_PASS = HOST + "/admin_change_pswd"
ADMIN_DELETE_USER = HOST + "/admin_delete_user"
ADMIN_ADD_USER = HOST + "/admin_add_user"
ADMIN_GET_USER_INFO = HOST + "/admin_get_user_info"
ADMIN_GET_STATS = HOST + "/admin_get_stats"
ADMIN_USER_DELETES = HOST + "/admin_user_deletes"
ADMIN_GET_USER_LOGS = HOST + "/admin_get_user_logs"
ADMIN_GET_USER_OPS = HOST + "/admin_get_user_operations"

GlobalUpdateManagerNum = Value('i', 0) #0 is False, 1 is True
GlobalAutoUpdate = Value('i', 1) #0 is UserUpdate, 1 is AutoUpdate
GlobalChangeUpdate = Value('i', 0) #0 is don't change, 1 is change
GlobalUserNumber = 0

class FileHandler():

    def __init__(self, followDirectory):
        self.directory = followDirectory
        self.NameOfFile = 'CS3240FinalProject'

    def remove_adjacentRepeats(self, list):
        i = 1
        while (i < len(list)):
            if(list[i] == list[i-1]):
                list.pop(i)
                i -= 1
            i += 1
        return list

    def autoOrganizeFile(self, changes):

        #This works fine for everything except when new directories and files (or combination of both) are moved in. To work around this,
        # I am going to add extra logic that ignores the "create" part of these new files copied in and instead declare a None in the first part
        # of the move command. This will then have to be taken care of by the server...

        DirectionListInOrder = []
        if(changes[0:4] == 'File'):
            if(changes[6:14] == 'modified'):
                fileValue = changes.find(self.NameOfFile)
                if (len(str.strip(changes[fileValue + len(self.NameOfFile):])) > 0):
                    DirectionListInOrder.append('Transfer: ' + changes[fileValue + len(self.NameOfFile):])
            elif(changes[6:13] == 'deleted'):
                fileValue = changes.find(self.NameOfFile)
                DirectionListInOrder.append('Delete: ' + changes[fileValue + len(self.NameOfFile):])
            elif(changes[6:11] == 'moved'):
                fileValueOne = changes.find(self.NameOfFile)
                fileValueTwo = changes.find(self.NameOfFile, fileValueOne + len(self.NameOfFile))
                fileValueComma = changes.find(',', fileValueOne + len(self.NameOfFile))
                if (len(str.strip(changes[fileValueOne + len(self.NameOfFile):fileValueComma])) == 0):
                    DirectionListInOrder.append('Move: ' + "None" + ' to ' + changes[fileValueTwo + len(self.NameOfFile):])
                else:
                    DirectionListInOrder.append('Move: ' + changes[fileValueOne + len(self.NameOfFile):fileValueComma] + ' :to: ' + changes[fileValueTwo + len(self.NameOfFile):])
        else:
            if(changes[11:18] == 'created'):
                fileValue = changes.find(self.NameOfFile)
                if (len(str.strip(changes[fileValue + len(self.NameOfFile):])) > 0):
                    DirectionListInOrder.append('DirCreate: ' + changes[fileValue + len(self.NameOfFile):])
            elif(changes[11:18] == 'deleted'):
                fileValue = changes.find(self.NameOfFile)
                DirectionListInOrder.append('DirDelete: ' + changes[fileValue + len(self.NameOfFile):])
            elif(changes[11:16] == 'moved'):
                fileValueOne = changes.find(self.NameOfFile)
                fileValueTwo = changes.find(self.NameOfFile, fileValueOne + len(self.NameOfFile))
                fileValueComma = changes.find(',', fileValueOne + len(self.NameOfFile))
                if (len(str.strip(changes[fileValueOne + len(self.NameOfFile):fileValueComma])) == 0):
                    DirectionListInOrder.append('DirMove: ' + "None" + ' to ' + changes[fileValueTwo + len(self.NameOfFile):])
                else:
                    DirectionListInOrder.append('DirMove: ' + changes[fileValueOne + len(self.NameOfFile):fileValueComma] + ' :to: ' + changes[fileValueTwo + len(self.NameOfFile):])

        finalList = self.remove_adjacentRepeats(DirectionListInOrder)
        for values in finalList:
            dic = {'Value': values}
            theFile = {}
            if "Transfer: " in values:
                stringFileName = values[11:]
                theFile = {'file': open(stringFileName, 'rb')}
            string = requests.post(COMMAND, headers=dic, files=theFile)
        	#print string.text
        return finalList

    def organizeFile(self):

        #This works fine for everything except when new directories and files (or combination of both) are moved in. To work around this,
        # I am going to add extra logic that ignores the "create" part of these new files copied in and instead declare a None in the first part
        # of the move command. This will then have to be taken care of by the server...

        lines = [line.strip() for line in open(self.directory)]
        DirectionListInOrder = []
        for changes in lines:
            if(changes[0:4] == 'File'):
                if(changes[6:13] == 'created' or changes[6:14] == 'modified'):
                    fileValue = changes.find(self.NameOfFile)
                    if (len(str.strip(changes[fileValue + len(self.NameOfFile):])) > 0):
                        DirectionListInOrder.append('Transfer: ' + changes[fileValue + len(self.NameOfFile):])
                elif(changes[6:13] == 'deleted'):
                    fileValue = changes.find(self.NameOfFile)
                    DirectionListInOrder.append('Delete: ' + changes[fileValue + len(self.NameOfFile):])
                elif(changes[6:11] == 'moved'):
                    fileValueOne = changes.find(self.NameOfFile)
                    fileValueTwo = changes.find(self.NameOfFile, fileValueOne + len(self.NameOfFile))
                    fileValueComma = changes.find(',', fileValueOne + len(self.NameOfFile))
                    if (len(str.strip(changes[fileValueOne + len(self.NameOfFile):fileValueComma])) == 0):
                        DirectionListInOrder.append('Move: ' + "None" + ' to ' + changes[fileValueTwo + len(self.NameOfFile):])
                    else:
                        DirectionListInOrder.append('Move: ' + changes[fileValueOne + len(self.NameOfFile):fileValueComma] + ' :to: ' + changes[fileValueTwo + len(self.NameOfFile):])
            else:
                if(changes[11:18] == 'created'):
                    fileValue = changes.find(self.NameOfFile)
                    if (len(str.strip(changes[fileValue + len(self.NameOfFile):])) > 0):
                        DirectionListInOrder.append('DirCreate: ' + changes[fileValue + len(self.NameOfFile):])
                elif(changes[11:18] == 'deleted'):
                    fileValue = changes.find(self.NameOfFile)
                    DirectionListInOrder.append('DirDelete: ' + changes[fileValue + len(self.NameOfFile):])
                elif(changes[11:16] == 'moved'):
                    fileValueOne = changes.find(self.NameOfFile)
                    fileValueTwo = changes.find(self.NameOfFile, fileValueOne + len(self.NameOfFile))
                    fileValueComma = changes.find(',', fileValueOne + len(self.NameOfFile))
                    if (len(str.strip(changes[fileValueOne + len(self.NameOfFile):fileValueComma])) == 0):
                        DirectionListInOrder.append('DirMove: ' + "None" + ' to ' + changes[fileValueTwo + len(self.NameOfFile):])
                    else:
                        DirectionListInOrder.append('DirMove: ' + changes[fileValueOne + len(self.NameOfFile):fileValueComma] + ' :to: ' + changes[fileValueTwo + len(self.NameOfFile):])

        finalList = self.remove_adjacentRepeats(DirectionListInOrder)
        for values in finalList:
            dic = {'Value': values}
            theFile = {}
            if "Transfer: " in values:
                stringFileName = values[11:]
                theFile = {'file': open(stringFileName, 'rb')}
            string = requests.post(COMMAND, headers=dic, files=theFile)
            #print string.text
        open("../DoNotDelete.txt", 'w').close()
        return finalList

class MyThread(threading.Thread):
	def run(self):
		while(True):
			updateOrNot = raw_input("Type in anything and press enter to update: ")
			if((len(updateOrNot) >= 0)):
				HandlingFiles = FileHandler("../DoNotDelete.txt")
				HandlingFiles.organizeFile()

class MyHandler(FileSystemEventHandler):

    currentEvent = ""
    update = True

    def on_modified(self, event):
        super(MyHandler, self).on_modified(event)
        what = 'Directory' if event.is_directory else 'File'
        self.currentEvent = what + ", modified, " + event.src_path
        if(self.update == False):
            file = open("../DoNotDelete.txt", "a+")
            file.write(self.currentEvent + "\n")
            file.close()
        else:
            TheFileHandler = FileHandler("../DoNotDelete.txt")
            TheFileHandler.autoOrganizeFile(self.currentEvent)

    def on_created(self, event):
        super(MyHandler, self).on_created(event)
        what = 'Directory' if event.is_directory else 'File'
        self.currentEvent = what + ", created, " + event.src_path
        if(self.update == False):
            file = open("../DoNotDelete.txt", "a+")
            file.write(self.currentEvent + "\n")
            file.close()
        else:
            TheFileHandler = FileHandler("../DoNotDelete.txt")
            TheFileHandler.autoOrganizeFile(self.currentEvent)

    def on_deleted(self, event):
        super(MyHandler, self).on_deleted(event)
        what = 'Directory' if event.is_directory else 'File'
        self.currentEvent = what + ", deleted, " + event.src_path
        if(self.update == False):
            file = open("../DoNotDelete.txt", "a+")
            file.write(self.currentEvent + "\n")
            file.close()
        else:
            TheFileHandler = FileHandler("../DoNotDelete.txt")
            TheFileHandler.autoOrganizeFile(self.currentEvent)

    def on_moved(self, event):
        super(MyHandler, self).on_moved(event)
        what = 'Directory' if event.is_directory else 'File'
        if(event.src_path is None): # Means that a file(s) has been moved into the OneDir Folder.
            currentPath = os.path.dirname(os.path.realpath(__file__))
            self.currentEvent = what + ", created, " + currentPath + "\n" + what + ", moved, from: " + currentPath + ", to: " + event.dest_path
        else:
            self.currentEvent = what + ", moved, from: " + event.src_path + ", to: " + event.dest_path
        if(self.update == False):
            file = open("../DoNotDelete.txt", "a+")
            file.write(self.currentEvent + "\n")
            file.close()
        else:
            TheFileHandler = FileHandler("../DoNotDelete.txt")
            TheFileHandler.autoOrganizeFile(self.currentEvent)

    def get_boolean(self, bool):
        self.update = bool

class MainPage():

    def __init__(self, followDirectory):
        self.directory = followDirectory
        self.NameOfFile = 'GautamOneDir'

    def CheckUser(self):
        string = requests.post(CHECK_USER)
        if(string.text == ""):
            return False
        return True

    def LogInPartOne(self):
        StringUserName = None
        StringPassword = None
        global GlobalUserNumber
        print("If this is your first time running OneDir and you want to make an account, simply type in 'new' for both the UserName and Password...")
        while(True):
            userName = raw_input("UserName: ")
            try:
                StringUserName = str(userName)
                break
            except:
                print "Not a valid UserName input."
        while(True):
            password = raw_input("Password: ")
            try:
                StringPassword = str(password)
                break
            except:
                print "Not a valid password input."
        userDict = {'UserName': StringUserName, 'Password': StringPassword}
        boolValue = True
        if(StringUserName == 'new' and StringPassword == 'new'):
            temp = self.AddNewUser()
            if(temp[0] == "Username already in use!"):
                boolValue = False
            userDict = {'UserName': temp[2], 'Password': temp[3]}
        if(boolValue == True):
            string = requests.post(LOGIN_URL, headers=userDict)
            returnBool = False;
            if("Login Successful" in str(string.text)):
                returnBool = True
                indexOfPar = str(string.text).find("(")
                indexOfPar2 = str(string.text).find(")")
                intInString = str(string.text)[indexOfPar+1:indexOfPar2]
                GlobalUserNumber = int(intInString)
                print str(GlobalUserNumber)
            return (string.text, returnBool);
        else:
            return ("Username already in use!", False)

    def alternativeLogIn(self):
        StringUserName = None
        StringPassword = None
        while(True):
            print "One login session is already in session, so you must login with the same credentials."
            userName = raw_input("UserName: ")
            try:
                StringUserName = str(userName)
                break
            except:
                print "Not a valid UserName input."
        while(True):
            password = raw_input("Password: ")
            try:
                StringPassword = str(password)
                break
            except:
                print "Not a valid password input."
        userDict = {'UserName': StringUserName, 'Password': StringPassword}
        string = requests.post(ALT_LOGIN, headers=userDict)
        returnBool = False;
        if("Login Successful" in str(string.text)):
            returnBool = True;
            indexOfPar = str(string.text).find("(")
            indexOfPar2 = str(string.text).find(")")
            intInString = str(string.text)[indexOfPar+1:indexOfPar2]
            GlobalUserNumber = int(intInString)
            print str(GlobalUserNumber)
        return (string.text, returnBool);

    def AddNewUser(self):
        StringUserName = None
        StringPassword = None
        while(True):
            print "Adding a new User..."
            userName = raw_input("New UserName: ")
            try:
                StringUserName = str(userName)
                break
            except:
                print "Not a valid UserName input."
        while(True):
            password = raw_input("New Password: ")
            try:
                StringPassword = str(password)
                break
            except:
                print "Not a valid password input."
        userDict = {'UserName': StringUserName, 'Password': StringPassword}
        string = requests.post(ADD_USER_URL, headers=userDict)
        returnBool = False;
        if(str(string.text) == "Username Added"):
            returnBool = True;
        return (string.text, returnBool, StringUserName, StringPassword)

    def AddNewUserAdmin(self):
        userName = requests.post(CHECK_USER)
        if 'Admin/' in userName.text:
            print "Admin Confirmed."
            print "Okay, time to add a new user..."
            print "If you want this user to be add an admin, simply add Admin/ to the front of the UserName."

            while(True):
                adminPass = raw_input("Admin Password: ")
                try:
                    adminPW = str(adminPass)
                    break
                except:
                    print "Not a valid input format."
            while(True):
                userNameToChange = raw_input("Username to Add: ")
                try:
                    userID = str(userNameToChange)
                    break
                except:
                    print "Not a valid input format."
            while(True):
                newPass = raw_input("Password of new User: ")
                try:
                    userPW = str(newPass)
                    break
                except:
                    print "Not a valid input format."
            userDict = {'AdminID': userName.text,'AdminPW': adminPW, 'UserName': userID, 'NewPass': userPW}
            string = requests.post(ADMIN_ADD_USER, headers=userDict)
            boolean = False
            if(string.text == "Username Added"):
                return True
            print string.text
            return (string.text, boolean)
        else:
            print "This is an Admin-Only command!"

    def logout(self):
        string = requests.post(LOGOUT)
        return ("Logout", True)

    def change_password(self):
        userName = requests.post(CHECK_USER)
        StringNew = None
        StringOld = None
        print "Okay, time to change your password..."
        while(True):
            oldPass = raw_input("Old Password: ")
            try:
                StringOld = str(oldPass)
                break
            except:
                print "Not a valid input format."
        while(True):
            newPass = raw_input("New Password: ")
            try:
                StringNew = str(newPass)
                break
            except:
                print "Not a valid input format."
        userDict = {'UserName': userName.text, 'OldPass': StringOld, 'NewPass': StringNew}
        string = requests.post(CHANGE_PASS, headers=userDict)
        boolean = False
        if(string.text == "Password Changed"):
            return True
        return (string.text, boolean)

    def change_another_user_password(self):
        userName = requests.post(CHECK_USER)
        if 'Admin/' in userName.text:
            print "Admin Confirmed."
            print "Okay, time to change another user's password..."

            while(True):
                adminPass = raw_input("Admin Password: ")
                try:
                    adminPW = str(adminPass)
                    break
                except:
                    print "Not a valid input format."
            while(True):
                userNameToChange = raw_input("Username to Change: ")
                try:
                    userID = str(userNameToChange)
                    break
                except:
                    print "Not a valid input format."
            while(True):
                newPass = raw_input("New Password: ")
                try:
                    userPW = str(newPass)
                    break
                except:
                    print "Not a valid input format."
            userDict = {'AdminID': userName.text,'AdminPW': adminPW, 'UserName': userID, 'NewPass': userPW}
            string = requests.post(ADMIN_CHANGE_PASS, headers=userDict)
            boolean = False
            if(string.text == "Password Changed"):
                return True
            return (string.text, boolean)
        else:
            print "This is an Admin-Only command!"

    def delete_user(self):
        userName = requests.post(CHECK_USER)
        filesToo = "False"
        if 'Admin/' in userName.text:
            print "Admin Confirmed."
            print "Okay, time to delete another user..."

            while(True):
                adminPass = raw_input("Admin Password: ")
                try:
                    adminPW = str(adminPass)
                    break
                except:
                    print "Not a valid input format."
            while(True):
                userNameToChange = raw_input("Username to Delete: ")
                try:
                    userID = str(userNameToChange)
                    break
                except:
                    print "Not a valid input format."
            while(True):
                deleteFilesToo = raw_input("Should we delete the files as well (y/n): ")
                try:
                    filesTooString = str(deleteFilesToo)
                    if(filesTooString == 'n'):
                        break
                    if(filesTooString == 'y'):
                        filesToo = "True"
                        break
                    else:
                        print "Not a valid y or n."
                except:
                    print "Not a valid input format."
            userDict = {'AdminID': userName.text,'AdminPW': adminPW, 'UserName': userID, 'FilesToo': filesToo}
            #userDict = {'AdminID': userName.text,'AdminPW': adminPW, 'UserName': userID}
            string = requests.post(ADMIN_DELETE_USER, headers=userDict)
            boolean = False
            print string.text
            if(string.text == "User <" + userID + "> Deleted"):
                return True
            return (string.text, boolean)
        else:
            print "This is an Admin-Only command!"

    def admin_get_user_info(self):
            userName = requests.post(CHECK_USER)
            if 'Admin/' in userName.text:
                print "Admin Confirmed."

                while(True):
                    adminPass = raw_input("Admin Password: ")
                    try:
                        adminPW = str(adminPass)
                        break
                    except:
                        print "Not a valid input format."
                while(True):
                    userNameToChange = raw_input("Username you want information for: ")
                    try:
                        userID = str(userNameToChange)
                        break
                    except:
                        print "Not a valid input format."
                userDict = {'AdminID': userName.text,'AdminPW': adminPW, 'UserName': userID}
                string = requests.post(ADMIN_GET_USER_INFO, headers=userDict)
                boolean = False
                if(string.text != "That UserName doesn't exist." and string.text != "Wrong Admin Password" and string.text != "Error in the Program with getting user info..."):
                    print
                    print
                    print "***** Here is the users information *****"
                    print
                    print "For UserName " + userID + " the password is " + string.text
                    print
                    print "***** End of information *****"
                    print
                    print
                    return True
                return (string.text, boolean)
            else:
                print "This is an Admin-Only command!"

    def admin_get_stats(self):
            userName = requests.post(CHECK_USER)
            if 'Admin/' in userName.text:
                print "Admin Confirmed."

                while(True):
                    adminPass = raw_input("Admin Password: ")
                    try:
                        adminPW = str(adminPass)
                        break
                    except:
                        print "Not a valid input format."
                while(True):
                    userNameToChange = raw_input("Username you want statistics for (type total for total information): ")
                    try:
                        userID = str(userNameToChange)
                        break
                    except:
                        print "Not a valid input format."
                userDict = {'AdminID': userName.text,'AdminPW': adminPW, 'UserName': userID}
                string = requests.post(ADMIN_GET_STATS, headers=userDict)
                if(string.text != "That UserName doesn't exist." and string.text != "Wrong Admin Password" and string.text != "Error in the Program with getting user info..."):
                    print
                    print
                    print "***** Here is the users statistics *****"
                    print
                    print string.text
                    print
                    print "***** End of statistics *****"
                    print
                    print
                    return True
                print
                print string.text
                print
                return (string.text, False)
            else:
                print "This is an Admin-Only command!"

    def admin_user_deletes(self):
        userName = requests.post(CHECK_USER)
        if 'Admin/' in userName.text:
            print "Admin Confirmed."
            while(True):
                adminPass = raw_input("Admin Password: ")
                try:
                    adminPW = str(adminPass)
                    break
                except:
                    print "Not a valid input format."
            userDict = {'AdminID': userName.text,'AdminPW': adminPW}
            string = requests.post(ADMIN_USER_DELETES, headers=userDict)
            if(string.text != "Wrong Admin Password" and string.text != "Error in the Program with getting user info..."):
                print
                print
                print "***** Here are the users that have been deleted so far *****"
                print
                print string.text
                print "***** End of list *****"
                print
                print
                return True
            print
            print string.text
            print
            return (string.text, False)
        else:
            print "This is an Admin-Only command!"

    def admin_get_user_logs(self):
            userName = requests.post(CHECK_USER)
            if 'Admin/' in userName.text:
                print "Admin Confirmed."
                OpsTrueLogsFalse = ""
                OpsTotalOrUser = ""
                userID = ""

                while(True):
                    adminPass = raw_input("Admin Password: ")
                    try:
                        adminPW = str(adminPass)
                        break
                    except:
                        print "Not a valid input format."
                while(True):
                    userNameToChange = raw_input("Do you want the logs or operations (logs/operations): ")
                    try:
                        OpsTrueLogsFalse = str(userNameToChange).strip().lower()
                        if(OpsTrueLogsFalse == "logs" or OpsTrueLogsFalse == "operations"):
                            break
                        else:
                            print "You have to say \'logs\' or \'operations\'."
                    except:
                        print "Not a valid input format."
                if(OpsTrueLogsFalse == "operations"):
                    while(True):
                        userNameToChange = raw_input("Do you want the total operations or just a user (total/user): ")
                        try:
                            OpsTotalOrUser= str(userNameToChange).strip().lower()
                            if(OpsTotalOrUser == "total" or OpsTotalOrUser == "user"):
                                break
                            else:
                                print "You have to say \'total\' or \'user\'."
                        except:
                            print "Not a valid input format."
                if(OpsTotalOrUser != "total"):
                    while(True):
                        userNameToChange = raw_input("Username you want logs/information for: ")
                        try:
                            userID = str(userNameToChange).strip()
                            break
                        except:
                            print "Not a valid input format."

                userDict1 = {'AdminID': userName.text,'AdminPW': adminPW, 'UserName': userID}
                userDict2 = {'AdminID': userName.text,'AdminPW': adminPW, 'UserName': userID, 'OpsTotal': OpsTotalOrUser}

                if(OpsTrueLogsFalse == "operations"):
                    string = requests.post(ADMIN_GET_USER_OPS, headers=userDict2)
                else:
                    string = requests.post(ADMIN_GET_USER_LOGS, headers=userDict1)
                boolean = False
                if(string.text != "That UserName doesn't exist." and string.text != "Wrong Admin Password" and string.text != "Error in the Program with getting user info..."):
                    print
                    print
                    print "***** Here is the users information *****"
                    print
                    print "For UserName " + userID + " the password is " + string.text
                    print
                    print "***** End of information *****"
                    print
                    print
                    return True
                print string.text
                return (string.text, boolean)
            else:
                print "This is an Admin-Only command!"


# The following two processes deal with the WatchDog commands being sent to the server.
def runOneAuto():
    event_handler = MyHandler()
    event_handler.get_boolean(True)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

########### HAVE TO FIGURE OUT HOW TO TRANSFER VARIABLES ACROSS PROCESSES SO THAT I CAN SWITCH BETWEEN THESE TWO...

def runOneUser():
	event_handler = MyHandler()
	event_handler.get_boolean(False)
	observer = Observer()
	observer.schedule(event_handler, path='.', recursive=True)
	observer.start()
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		observer.stop()
	observer.join()

# This is a helper method that deals with user input for auto-updating.
def runOneUserA():
	global GlobalUpdateManagerNum
	while(True):
		if(GlobalUpdateManagerNum.value == 1):
			HandlingFiles = FileHandler("../DoNotDelete.txt")
			HandlingFiles.organizeFile()
			GlobalUpdateManagerNum.value = 0

def checkUpdateSettings(p1, p2, p3): #p1 is AutoUpdate process, p2, p3 is User Update Process
	global GlobalAutoUpdate
	global GlobalChangeUpdate
	while(True):
		if(GlobalChangeUpdate.value == 1):
			if(GlobalAutoUpdate.value == 1):
				p2.terminate()
				p3.terminate()
				p1.start()
				p1.join()
			else:
				p1.terminate()
				p2.start()
				p3.start()
				p2.join()
				p3.join()
			GlobalChangeUpdate.value == 0

############# THEN I HAVE TO IMPLEMENT THAT HERE, WITH A VARIATION OF SHUTTING DOWN ONE PROCESS AND LAUNCHING ANOTHER, SO THAT I CAN SWITCH BETWEEN THE TWO
# The following process deals with the user interface on the client side.
def runTwo():
    global GlobalUpdateManagerNum
    global GlobalAutoUpdate
    global GlobalChangeUpdate
    TheFileHandler = FileHandler("../DoNotDelete.txt")
    AutoUpdate = True
    run = MainPage("../DoNotDelete.txt")
    while (True):
        print "  (1) Type a 1 to logout."
        print "  (2) Type a 2 to change your password."
        print "  (3) Type a 3 to switch between Auto-Update being on or off."
        print "  (4)  **Admin-Only** Type a 4 to add a new user."
        print "  (5)  **Admin-Only** Type a 5 to change another user's password."
        print "  (6)  **Admin-Only** Type a 6 to delete another user."
        print "  (7)  **Admin-Only** Type a 7 to get information about a user."
        print "  (8)  **Admin-Only** Type a 8 to get statistics about a user (or total statistics)."
        print "  (9)  **Admin-Only** Type a 9 to get a list of all the users that have been deleted."
        print "  (10) **Admin-Only** Type a 10 to get logs or operations of OneDir."
        print " * If you are in User Update mode, simply input 'update' to perform a server update * "
        while (True):
            userInstruction = raw_input("Input: ")
            try:
                StringInput = str(userInstruction)
                break
            except:
                print "Not a valid input format."
        if (StringInput.strip() == "1"):
            run.logout()
            print ""
            print ""
            print "Thanks for using OneDir..."
            print ""
            print ""
            time.sleep(2)
            print "Please press Ctrl-C to exit completely."
            break
        elif (StringInput.strip() == "2"):
            run.change_password()
        elif (StringInput.strip() == "3"):
            if (AutoUpdate):
                doWeUpdate = raw_input("Auto Update is currently on. Would you like to turn it off (y/n): ")
                try:
                    if (str(doWeUpdate).strip().lower() == 'y'):
                        AutoUpdate = False
                        GlobalAutoUpdate.value = 0
                        GlobalChangeUpdate.value = 1
                except:
                    print "Not a valid input form"
            else:
                doWeUpdate = raw_input("Auto Update is currently off. Would you like to turn it on (y/n): ")
                try:
                    if (str(doWeUpdate).strip().lower() == 'y'):
                        AutoUpdate = True
                        GlobalAutoUpdate.value = 1
                        GlobalChangeUpdate.value = 1
                except:
                    print "Not a valid input form"
        elif (StringInput.strip() == "4"):
            run.AddNewUserAdmin()
        elif (StringInput.strip() == "5"):
            run.change_another_user_password()
        elif (StringInput.strip() == "6"):
            run.delete_user()
        elif(StringInput.strip() == "7"):
            run.admin_get_user_info()
        elif(StringInput.strip() == "8"):
            run.admin_get_stats()
        elif(StringInput.strip() == "9"):
            run.admin_user_deletes()
        elif(StringInput.strip() == "10"):
            run.admin_get_user_logs()
        elif(StringInput.strip().lower() == "testupdate"):
            userDict = {"Number": str(GlobalUserNumber)}
            print requests.post(GET_UPDATE, headers=userDict).text
        elif(StringInput.strip().lower() == "testfile"):
            userDict = {"Path": "login_info.txt"}
            theFile = requests.post(GET_FILE, headers=userDict)
            print theFile.content
        elif (StringInput.strip().lower() == "update"):
            TheFileHandler.organizeFile()
        elif(StringInput.strip().lower() == "test"):
            userDict = {'command': "This is the command..."}
            test = {'file': open('test.txt', 'rb')}
            requests.post(FILE_TRANSFER, files=test, headers=userDict)
        else:
            print "Not a valid input. Please try again, or input 1 to logout."

if __name__ == "__main__":
	run = MainPage("../DoNotDelete.txt")
	theBool = run.CheckUser()
	print "Welcome to One Direction... the better version of DropBox."
	while(True):
		if(theBool == False):
			string = run.LogInPartOne()
		else:
			string = run.alternativeLogIn()

		if(string[1] == True):
			break
        else:
            if(string[0] == "Username already in use!"):
                print "Username already in use!"
            else:
                print "Invalid Login"
	print "You are now logged in... Congratulations."
	print "You now have a breadth of options..."

	p1 = Process(target=runOneAuto)
	p2 = Process(target=runOneUser)
	p3 = Process(target=runOneUserA)
	p4 = threading.Thread(target=runTwo)
	p4.daemon = True
	p5 = Process(target=checkUpdateSettings, args=(p1, p2, p3))

	p2.start()
	p4.start()
	p5.start()

	p2.join()
	p4.join()
	p5.join()