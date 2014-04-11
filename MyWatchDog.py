import sys
import time
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#Have to change the value of self.NameOfFile in the FileHandler() class in order for this to work if you move it to another file.

################################# UPDATE LIST FOR WATCHDOG FILE ##########################################################################

########### As of April 1st ....

#Things for me to do...
#   Create a class that deals with transfering files or commands (based on transfer or deletion or movement).
#   Then integrate the class in two places. First with the MyHandler() on the else case for auto-updating.
#   Second with the FileHandler() classes finalList return object from the organizeFiles() method.

# Look into the Cut and Paste Comment in the FileHandler() class

# Also look into how to deal with renames (has to do with the main path not really changing)

# Have to deal with recursive deletion of a folder... like how does this work and how do I look at it (repeated directory delete command).

########### As of April 10th...

# The WatchDog part seems to work fine with everything. Everything such as creation, deletion, movement, renaming, and recursive deleting is dealt
# with in a way that makes a lot of sense. Just have to integrate with the server...

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
                    DirectionListInOrder.append('Move: ' + changes[fileValueOne + len(self.NameOfFile):fileValueComma] + ' to ' + changes[fileValueTwo + len(self.NameOfFile):])
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
                    DirectionListInOrder.append('DirMove: ' + changes[fileValueOne + len(self.NameOfFile):fileValueComma] + ' to ' + changes[fileValueTwo + len(self.NameOfFile):])

        finalList = self.remove_adjacentRepeats(DirectionListInOrder)
        for values in finalList:
            print values
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
                        DirectionListInOrder.append('Move: ' + changes[fileValueOne + len(self.NameOfFile):fileValueComma] + ' to ' + changes[fileValueTwo + len(self.NameOfFile):])
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
                        DirectionListInOrder.append('DirMove: ' + changes[fileValueOne + len(self.NameOfFile):fileValueComma] + ' to ' + changes[fileValueTwo + len(self.NameOfFile):])

        finalList = self.remove_adjacentRepeats(DirectionListInOrder)
        print "List \n"
        for values in finalList:
            print values
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
    update = False

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

if __name__ == "__main__":
    booleanUpdate = False
    updateOrNot = raw_input("Would you like to enable auto-update (y/n): ")
    if((len(updateOrNot) == 1) and (updateOrNot.lower() == "y")):
        booleanUpdate = True
    event_handler = MyHandler()
    event_handler.get_boolean(booleanUpdate)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    if(booleanUpdate == False):
        t = MyThread()
        t.daemon = True
        t.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()