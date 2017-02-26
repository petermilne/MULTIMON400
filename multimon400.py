#!/usr/local/bin/python
import pexpect
import threading
import time

class Uut:
    def __init__(self, _name):
        self.name = _name
        self.ip = "0.0.0.0"
        self.epics_hn = "acq1001_000"
        
    def init(self):
        ping = pexpect.spawn("ping -c1 %s" % self.name)
        
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.name == other.name  
    def __repr__(self):
        return "Uut(%s, %s, %s)" % (self.name, self.ip, self.epics_hn)
    
def cas_mon():
    casw = pexpect.spawn("casw -i 10")

    CASWSTAT = "  ([\w\.]+):5064.*$"

    while True:
        match = casw.expect([CASWSTAT, pexpect.EOF, pexpect.TIMEOUT])
        if match == 0:
            yield casw.match.group(1)        
        elif match == 1:
            print "EOF"
            break
        elif match == 2:
            print "Timeout"
            continue
   
uuts = set()     

def uut_mon():  
    global uuts
    for i in cas_mon():
        uut = Uut(i)
        if not uut in uuts:
            print("New: %s" % uut)
            uuts.add(uut)
        
    

uut_monitor = threading.Thread(target=uut_mon)
uut_monitor.setDaemon(True)
uut_monitor.start()

while True:
    print( "Hello %s" % uuts )
    for uut in uuts:
        print("Do CAGET %s:SYS:UPTIME HERE" % uut)
    time.sleep(1)



    
    

    
    
