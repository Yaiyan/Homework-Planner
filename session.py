import hashlib
import Cookie
import shelve
import random
import time
import os

class Session:
    """A simple wrapper around a few python modules which makes session
    handling a bit easier for me - reduces the number of lines of code needed
    in each file and allows easy access of session values
    
    - Original code written by Ieuan Jones (0147) for module CG2,
    reused for CG4"""
    
    def __init__(self):
        """Initialise the session class"""
        self.cookie = Cookie.SimpleCookie()
        self.newSession = True
        self.sid = -1
        
        self.cookieExists = False
    
    def load(self):
        """Check to see if any cookies have been set on the users computer.
        If so, renew the cookie and set user as logged in"""
        string_cookie = os.environ.get("HTTP_COOKIE")
        
        if string_cookie:
            self.cookie.load(string_cookie)
            self.sid = self.cookie["SID"].value
            self.cookie["SID"]["expires"] = 120*60 #Let's let it last for 2 hours
            self.newSession = False
            self.cookieExists = True
    
    def startNewSession(self, key):
        """Starts a new session and sets a cookie on the users computer which
        points to the session value. This allows the user to remain logged in.
        Sets the cookie to expire 120 minutes after creation."""
        self.sid = hashlib.sha512(str(time.time()*1000)+key+str(random.randint(0,100000))).hexdigest()
        self.cookie["SID"] = self.sid
        self.cookie["SID"]["expires"] = 120*60
        self.newSession = True
        self.cookieExists = True
    
    def setCookie(self):
        """Sends the HTTP headers required to set a cookie"""
        if self.cookieExists:
            print self.cookie
    
    def getSessionValue(self,id):
        """Get the value with the given id from the session storage"""
        session = shelve.open("sessions/sess"+self.sid, writeback=True)
        value = session[id]
        session.close()
        
        return value
    
    def setSessionValue(self,id,value):
        """Set the given value to the given id in the session storage"""
        session = shelve.open("sessions/sess"+self.sid, writeback=True)
        session[id] = value
        session.close()
    
    def logout(self):
        """Logs the user out by setting the cookie to expire"""
        if self.cookieExists:
            self.cookie["SID"]["expires"] = 0