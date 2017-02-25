#!/usr/local/bin/python
import pexpect
import threading
import time

class Uut:
    def __init__(self, _name):
        self.name = _name
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
        if not i in uuts:
            print("New: %s" % i)
            uuts.add(i)
        
    

uut_monitor = threading.Thread(target=uut_mon)
uut_monitor.setDaemon(True)
uut_monitor.start()

while True:
    print( "Hello %s" % uuts )
    for uut in uuts:
        print("Do CAGET %s:SYS:UPTIME HERE" % uut)
    time.sleep(1)



    
    

    
    
