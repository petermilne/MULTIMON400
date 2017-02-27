#!/usr/local/bin/python
import pexpect
import threading
import time
import socket
import epics
import re
import sys
import time

class Uut:
    def query_ioc_name(self):
        ioc_name_pv = 'IP:' + re.sub('\.', ':', self.ip)
        pv = epics.PV(ioc_name_pv, 
                     connection_timeout=5)
        self.epics_hn = pv.get()
        print("self.epics_hn set %s" % self.epics_hn)
        
    def __init__(self, _name):
        self.pvs = {}
        self.delay = 0
        self.name = _name
        self.ip = socket.gethostbyname(self.name)
        if self.ip != self.name:                
            self.name = re.sub('\..*', '', self.name)
            
        self.query_ioc_name()
        if self.epics_hn == None:
            if self.ip != self.name:                                
                self.epics_hn = self.name                
            else:
                print("No epics hn for %s" % self)
                
        
            
            
        
    def init(self):
        ping = pexpect.spawn("ping -c1 %s" % self.name)
        
    def __hash__(self):
        return hash(self.name)
    def __lt__(self, other):
        return self.epics_hn.__lt__(other.epics_hn)
    
    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.name == other.name  
    def __repr__(self):
        return "Uut(%s, %s, %s)" % (self.name, self.ip, self.epics_hn)
    
    def on_update(self, **kws):
        self.pvs[re.sub(self.pv_trunc, '', kws['pvname'])] = kws['value']
        self.delay = 0
     
    def uut_status_update(self):
        for pvname in ( ':SYS:UPTIME', ':SYS:VERSION:SW', ':SYS:VERSION:FPGA', \
                        ':SYS:0:TEMP', ':1:SHOT', ':MODE:TRANS_ACT:STATE'):            
            epics.PV(self.epics_hn + pvname, auto_monitor=True, callback=self.on_update)        
        
    
    def start_monitor(self):
        self.pv_trunc = re.compile('.*:')
        self.monitor = threading.Thread(target=self.uut_status_update)
        self.monitor.setDaemon(True)
        self.monitor.start()
    
def cas_mon():
    casw = pexpect.spawn("casw -i 10")

    CASWSTAT = "  ([\w\.-]+):5064.*$"

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
            if uut.epics_hn != None:
                uuts.add(uut)
                uut.start_monitor()
    
    
# BAD BAD BAD: impose form on function, to cope with xsl sequence difficulty ..    
        
def xml_sequence(uut):
    try:
        for key in ('UPTIME', 'TEMP', 'STATE', 'SHOT', 'SW', 'FPGA'):
            yield (key, uut.pvs[key])
    except KeyError:
        return
        
            
    

uut_monitor = threading.Thread(target=uut_mon)
uut_monitor.setDaemon(True)
uut_monitor.start()

while True:  
    with open('multimon_acq400.xml', 'w') as xml:
        xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        xml.write("<body><header>{}</header>\n".format(time.strftime("%a, %d %b %T %Z %Y" )))
        for uut in sorted(uuts):
            xml.write("<record>\n")
            xml.write('<acq400monitor dt="1"/>\n')
            xml.write("<info>\n")        
            xml.write("<host>{}</host>\n".format(uut.epics_hn))
            
            for key, value in xml_sequence(uut):
                xml.write(" <{}>{}</{}>\n".format(key, value, key))
                            
            xml.write("</info>\n")
            xml.write("</record>\n")
            uut.delay += 1
            if uut.delay > 20:
                uuts.remove(uut)
            
        xml.write("</body>\n")
    time.sleep(1)



    
    

    
    
