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
    def __init__(self, name, pattern=None, email=None, sms=None,
                 phone=None, sms_carrier=None, jsonPath=None,
                 active=False, notifyByEmail=False, notifyBySMS=False):
        self.name = name
        self.email = email
        self.phone = phone
        self.sms_carrier = sms_carrier
        self.pattern = pattern
        self.jsonPath = jsonPath
        self.active = active
        self.notifyByEmail = notifyByEmail
        self.notifyBySMS = notifyBySMS
        self.prevState = QUIET
        self.active = active
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
        if not self.active:
            print "Skipping notification for %s because it is not activated" % self.name
            return
        print "Notifying %s" % self.name
        text = "Guides are available"
        if self.notifyByEmail:
            print " sending email to", self.email
            regSendMessage.sendMail(text, self.email)
        else:
            print  " email notification not activated"
        if self.notifyBySMS:
            print " sending SMS to", self.phone, self.sms_carrier
            regSendMessage.sendSMS(text, self.phone, self.sms_carrier)
        else:
            print  " SMS notification not activated"


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
                           active = obj.get("active", False),
                           email = obj.get('email'),
                           phone = obj.get('phone'),
                           notifyBySMS = obj.get('notifyBySMS', False),
                           notifyByEmail = obj.get('notifyByEmail', False),
                           sms_carrier = obj.get('sms_carrier'),
                           jsonPath = jsonPath)
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
        print "checking for updates to notification records"
        for ntf in list(self.notifications.values()):
            #print "ntf", ntf.jsonPath
            if ntf.jsonPath and not os.path.exists(ntf.jsonPath):
                print "Removing ntf", ntf.name, ntf.jsonPath
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
                print "============================================="
                print time.ctime()
                self.ndb.checkUpdates()
                print "----------------------------------------"
                self.update()
            except:
                traceback.print_exc()
            time.sleep(UPDATE_INTERVAL)

    def update(self):
        statusText = urllib2.urlopen(STATUS_URL).read()
        status = json.loads(statusText)
        print status
        for ntf in self.ndb.activeNotifications():
            ntf.observe(status)
        print

if __name__ == '__main__':
   ndb = NotificationDB()
   rw = RegistryWatcher(ndb)
   rw.run()

