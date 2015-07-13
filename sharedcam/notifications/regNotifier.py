#!/usr/bin/env python

import threading, time, traceback, os
import regSendMessage
import urllib2
import json

UPDATE_INTERVAL = 5
RECORDS_DIR = "records"
STATUS_URL = "http://sharedcam.paldeploy.com/registry/reg_query/"

QUIET = "Quiet"
ACTIVE = "Active"

class Notification:
    def __init__(self, name, pattern=None, email=None, sms=None, jsonPath=None):
        self.name = name
        self.email = email
        self.sms = sms
        self.pattern = pattern
        self.jsonPath = jsonPath
        self.prevState = QUIET
        self.mtime = time.time()

    def observe(self, regStatus):
        print "Notification %s observing" % (self.name)
        state = QUIET
        if self.matches(regStatus):
            state = ACTIVE
        if state == ACTIVE and self.prevState == QUIET:
            try:
                self.notify()
            except:
                traceback.print_exc()
        self.prevState = state

    def matches(self, regStatus):
        if len(regStatus['rooms']) > 0:
            return True
        return False

    def notify(self):
        print "Notifying %s" % self.name
        text = "Guides are available"
        if self.email:
            print " sending email to", self.email
            regSendMessage.sendMail(text, self.email)
        if self.sms:
            print " sending SMS to", self.sms
            regSendMessage.sendSMS(text, self.sms)


class NotificationDB:
    def __init__(self):
        self.notifications = {}
        self.checkUpdates()

    def activeNotifications(self):
        return self.notifications.values()

    def addNotification(self, ntf):
        self.notifications[ntf.name] = ntf

    def updateFromJSON_(self, jsonPath):
        #print "loadFromJSON", jsonPath
        fname = os.path.basename(jsonPath)[:-len(".json")]
        #print fname
        mtime = os.stat(jsonPath).st_mtime
        prevNtf = self.notifications.get(fname, None)
        if prevNtf != None:
            if  mtime < prevNtf.mtime:
                print "%s unchanged" % fname
                return
        obj = json.load(file(jsonPath))
        #print obj
        name = obj['name']
        if name != fname:
            print "*** Ignoring record %s with name not matching filename %s" % (name, fname)
            return
        ntf = Notification(name=name,
                           email = obj['email'], 
                           sms = obj['sms'])
        if prevNtf == None:
            print "%s - Adding new notfication" % name
            self.addNotification(ntf)
        else:
            print "%s - Updating notification" % name
            self.notifications[name] = ntf
            ntf.prevState = prevNtf.prevState


    def updateFromJSON(self, jsonPath):
        try:
            self.updateFromJSON_(jsonPath)
        except:
            print "*** Failed on", jsonPath
            traceback.print_exc()


    def checkUpdates(self):
        """
        First remove notifications whose files have vanished.
        """
        print "============================================="
        print "checking for updates to notification records"
        for ntf in list(self.notifications.values()):
            if ntf.jsonPath and not os.path.exists(ntf.jsonPath):
                print "Removing ntf"
                del self.notifications[ntf.name]

        print "NotificationDB checkUpdates"
        jsonFiles = os.listdir(RECORDS_DIR)
        for jsonFile in jsonFiles:
            if not jsonFile.lower().endswith(".json"):
                continue
            if jsonFile.find("#") >= 0:
                continue
            #print jsonFile
            jsonPath = os.path.join(RECORDS_DIR, jsonFile)
            self.updateFromJSON(jsonPath)

        
class RegistryWatcher:
    def __init__(self, ndb):
        self.rooms = []
        self.keepWatching = True
        self.ndb = ndb
    
    def runInThread(self):
        self.watcherThread = threading.Thread(target=self.run)
        self.watcherThread.setDaemon(True)
        self.watcherThread.start()

    def run(self):
        print "Watcher started!"
        while self.keepWatching:
            try:
                self.ndb.checkUpdates()
                self.update()
            except:
                traceback.print_exc()
            time.sleep(UPDATE_INTERVAL)

    def update(self):
        print "----------------------------------------"
        statusText = urllib2.urlopen(STATUS_URL).read()
        status = json.loads(statusText)
        print status
        for ntf in self.ndb.activeNotifications():
            ntf.observe(status)
        print

if __name__ == '__main__':
   ndb = NotificationDB()
   """
   ndb.addNotification(
       Notification("don", 
                    email="donkimber@gmail.com",
                    sms=("6502196316","ATT")))
   ndb.addNotification(Notification("bob"))
   """
   rw = RegistryWatcher(ndb)
   rw.run()

