import sys
import time
import os
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

#Have to change the value of self.NameOfFile in the FileHandler() class in order for this to work if you move it to another file.

#Things for me to do...
#   Create a class that deals with transfering files or commands (based on transfer or deletion or movement).
#   Then integrate the class in two places. First with the MyHandler() on the else case for auto-updating.
#   Second with the FileHandler() classes finalList return object from the organizeFiles() method.

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

    def organizeFile(self):
        lines = [line.strip() for line in open(self.directory)]
        DirectionListInOrder = []
        for changes in lines:
            if(changes[0:4] == 'File'):
                if(changes[6:13] == 'created' or changes[6:14] == 'modified'):
                    fileValue = changes.find(self.NameOfFile)
                    DirectionListInOrder.append('Transfer: ' + changes[fileValue + len(self.NameOfFile):])
                elif(changes[6:13] == 'deleted'):
                    fileValue = changes.find(self.NameOfFile)
                    DirectionListInOrder.append('Delete: ' + changes[fileValue + len(self.NameOfFile):])
                elif(changes[6:11] == 'moved'):
                    fileValueOne = changes.find(self.NameOfFile)
                    fileValueTwo = changes.find(self.NameOfFile, fileValueOne + len(self.NameOfFile))
                    fileValueComma = changes.find(',', fileValueOne + len(self.NameOfFile))
                    DirectionListInOrder.append('Move: ' + changes[fileValueOne + len(self.NameOfFile):fileValueComma] + ' to ' + changes[fileValueTwo + len(self.NameOfFile):])
            else:
                if(changes[11:18] == 'created'):
                    fileValue = changes.find(self.NameOfFile)
                    DirectionListInOrder.append('DirCreate: ' + changes[fileValue + len(self.NameOfFile):])
                elif(changes[11:18] == 'deleted'):
                    fileValue = changes.find(self.NameOfFile)
                    DirectionListInOrder.append('DirDelete: ' + changes[fileValue + len(self.NameOfFile):])
                elif(changes[11:16] == 'moved'):
                    fileValueOne = changes.find(self.NameOfFile)
                    fileValueTwo = changes.find(self.NameOfFile, fileValueOne + len(self.NameOfFile))
                    fileValueComma = changes.find(',', fileValueOne + len(self.NameOfFile))
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
            print self.currentEvent

    def on_created(self, event):
        super(MyHandler, self).on_created(event)
        what = 'Directory' if event.is_directory else 'File'
        self.currentEvent = what + ", created, " + event.src_path
        if(self.update == False):
            file = open("../DoNotDelete.txt", "a+")
            file.write(self.currentEvent + "\n")
            file.close()
        else:
            print self.currentEvent

    def on_deleted(self, event):
        super(MyHandler, self).on_deleted(event)
        what = 'Directory' if event.is_directory else 'File'
        self.currentEvent = what + ", deleted, " + event.src_path
        if(self.update == False):
            file = open("../DoNotDelete.txt", "a+")
            file.write(self.currentEvent + "\n")
            file.close()
        else:
            print self.currentEvent

    def on_moved(self, event):
        super(MyHandler, self).on_moved(event)
        what = 'Directory' if event.is_directory else 'File'
        self.currentEvent = what + ", moved, from: " + event.src_path + ", to: " + event.dest_path
        if(self.update == False):
            file = open("../DoNotDelete.txt", "a+")
            file.write(self.currentEvent + "\n")
            file.close()
        else:
            print self.currentEvent

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