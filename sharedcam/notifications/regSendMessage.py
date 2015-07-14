
import sys
import traceback
import smtplib

ERRMSG = """To use regSendMessage.py you must put a REG_CONFIG.py
somewhere in the python search path, and define FROM_ADDR and PASSWORD
"""

try:
    from REG_CONFIG import *
except:
    print ERRMSG
    sys.exit(1)

#FROM_ADDR = "wviewsmail@gmail.com"
#PASSWORD = "wviews1234"

GATEWAYS = {
   'att': "txt.att.net",
   "cricket": "mms.mycricket.com",
   "sprint": "messaging.sprintpcs.com",
   "tmobile": "tmomail.net",
   "uscellular": "email.uscc.net",
   "verizon": "vtext.com",
   "virgin": "vmobi.com",
}

def fixNumber(number):
    s = "%s" % number
    s = s.replace(",", "")
    s = s.replace("(", "")
    s = s.replace(")", "")
    s = s.replace(" ", "")
    return s

def getGateway(carrier):
    carrier = carrier.lower()
    carrier = carrier.replace(" ", "")
    carrier = carrier.replace("-", "")
    carrier = carrier.replace("&", "")
    carrier = carrier.replace(".", "")
    return GATEWAYS[carrier]

def sendSMS_(text, number, carrier):
   gateway = getGateway(carrier)
   fromAddr = FROM_ADDR
   toAddr = "%s@%s" % (fixNumber(number), gateway)
   print toAddr
   msg = "\r\n".join([
           "From: %s" % fromAddr,
           "To: %s" % toAddr,
           "Subject: WV Notification",
           text])
   print "msg:\n%s" % msg
   server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
   server_ssl.ehlo() # optional, called by login()
   
   server_ssl.login(fromAddr, PASSWORD)
   server_ssl.sendmail(fromAddr, toAddr, msg)
   #server_ssl.quit()
   server_ssl.close()
   print "Successfully sent SMS via mail"

def sendSMS(text, sms, carrier="ATT"):
    if type(sms) in [type((1,2)), type([1,2])]:
        number, carrier = sms
    else:
        number = sms
    try:
        sendSMS_(text, number, carrier)
    except:
        traceback.print_exc()


def sendMail_(text, toAddr):
   fromAddr = FROM_ADDR
   print "Send mail %s -> %s" %(fromAddr, toAddr)
   msg = "\r\n".join([
           "From: %s" % fromAddr,
           "To: %s" % toAddr,
           "Subject: WV Notification",
           text])
   print "msg:\n%s" % msg
   server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
   server_ssl.ehlo() # optional, called by login()
   server_ssl.login(fromAddr, PASSWORD)
   server_ssl.sendmail(fromAddr, toAddr, msg)
   #server_ssl.quit()
   server_ssl.close()
   print "Successfully sent mail"

def sendMail(text, toAddr):
    try:
        sendMail_(text, toAddr)
    except:
        traceback.print_exc()

def testSend():
   text = "Guide available.\nhttp://sharedcam.paldeploy.com\n"
   sendMail(text, "donkimber@gmail.com")
   sendSMS(text, "6502196316", "AT&T")

if __name__ == '__main__':
    testSend()






