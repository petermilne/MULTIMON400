
# site customization for multimon
import threading
import time
import urllib2
import re

TTYSERVERS = ('rpi-001', 'rpi-003', 'rpi-004', 'rpi-005', 'rpi-006', 'neon', 'eorsa', 'eigg')

def update_ttys(ttys, server):
    response = urllib2.urlopen('http://{}/cgi-bin/showconsoles.cgi'.format(server))
    html = response.read()
    for line in html.split('\n'):        
        match = re.match('tty_([a-zA-Z0-9_]+)', line)
        if (match):
#            print(match.group(1))
            ttys[match.group(1)] = server
    
def tty_mon(uuts):
    global TTYSERVERS
    ttys = {}
    
    while True:
        for server in TTYSERVERS:
            update_ttys(ttys, server)
            
        for uut in uuts: 
            try:
                uut.pvs['TTYHOST'] = ttys[uut.epics_hn]
            except:
                uut.pvs['TTYHOST'] = '...'
        time.sleep(2)
    
    
def register(TAGS, uuts):
    print("register")
    for uut in uuts:
        print("register {}".format(uut))
        
    TAGS.insert(0, ('TTYHOST', 'ttyhost'))
    tty_monitor = threading.Thread(target=tty_mon, args=(uuts, ))
    tty_monitor.setDaemon(True)
    tty_monitor.start()    