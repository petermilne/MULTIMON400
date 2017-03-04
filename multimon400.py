#!/usr/local/bin/python
import pexpect
import threading
import subprocess
import time
import socket
import epics
import re
import sys
import time
import os
import exceptions

class Uut:
    def query_ioc_name(self):
        ioc_name_pv = 'IP:' + re.sub('\.', ':', self.ip)
        pv = epics.PV(ioc_name_pv, 
                     connection_timeout=5.0)
        
        try:
            self.epics_hn = pv.get()
        except TypeError:
            print("TypeError : no worries")
        except ArgumentError:
            print("ArgumentError")
        
        
    def __init__(self, _name):
#        print("Uut {}".format(_name))
	self.pv_trunc = re.compile('.*:')
        self.pvs = {}	    # pv values
	self._PVS = []	    # pv instances
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
	                ':USER', ':TEST_DESCR', \
                        ':SYS:0:TEMP', ':1:SHOT', ':MODE:TRANS_ACT:STATE'):
	    self.pvs[re.sub(self.pv_trunc, '', pvname)] = '...'
            self._PVS.append(epics.PV(self.epics_hn + pvname, auto_monitor=True, callback=self.on_update))
	    	
	while self.delay < 60:
	    time.sleep(2.0)
	    	
	for pv in self._PVS:
	    pv.disconnect()
	    self._PVS.remove(pv)	
	 

def cas_mon():
    casw = subprocess.Popen(('casw', '-i', '2'), bufsize=-1, stdout=subprocess.PIPE)
    expr = re.compile('  ([]\w.-]+):5064')
    
    while True:
        out = casw.stdout.readline()
#        print("incoming:{}".format(out))
        if out == '' and process.poll() != None:
            break
        match = expr.search(out)
        if match != None:
#            print("yield:{}".format(match.group(1)))
            yield match.group(1)
            
uuts = set()     

def _uut_mon(hn):
    global uuts
#    print("_uut_mon() hn:{}".format(hn))
    uut = Uut(str(hn))
    if not uut in uuts:
        print("New: %s" % uut)
        if uut.epics_hn != None:
            uuts.add(uut)
	    uut.uut_status_update()
            
            
def uut_mon():  
    global uuts
    for hn in cas_mon():
#        print("uut_mon() hn:{}".format(hn))
        threading.Thread(target=_uut_mon, args=(hn, )).start()
    
    
# BAD BAD BAD: impose form on function, to cope with xsl sequence difficulty ..    
        
TAGS= [
    ('UPTIME', 'Uptime'),
    ('TEMP', 'T0'),
    ('STATE', 'State'),
    ('SHOT', 'Shot'),
    ('SW', 'Software'),
    ('FPGA', 'FPGA'),
    ('USER', 'User'),
    ('TEST_DESCR', 'Test')
]
    

def xml_sequence(uut):
    global TAGS
    try:
        for key, label in TAGS:
            yield (key, uut.pvs[key])
    except KeyError:
        return
   
def xml_headers():
    global TAGS
    for label in ('Delay', 'UUT'):
	yield label
    for key, label in TAGS:
	yield label
    
            
if os.getenv("MULTIMON_CUSTOM") != None:
    import multimon_custom
    multimon_custom.register(TAGS, uuts)

uut_monitor = threading.Thread(target=uut_mon)
uut_monitor.setDaemon(True)
uut_monitor.start()

DATFILE = 'multimon_acq400.xml'
DATFTMP = DATFILE + '.new'

while True:  
    with open(DATFTMP, 'w') as xml:
        xml.write('<?xml version="1.0" encoding="UTF-8"?>\n')
	xml.write("<body>\n")
	xml.write("    <header>\n")
        xml.write("        <ts>{}</ts>\n".format(time.strftime("%a, %d %b %T %Z %Y" )))
	xml.write("        <cheads>\n")
	for ch in xml_headers():	    
	    xml.write('            <h1>{}</h1>\n'.format(ch))	
	xml.write("        </cheads>\n")
	xml.write("     </header>\n")
        for uut in sorted(uuts):
            xml.write("    <record>\n")
            xml.write('        <acq400monitor dt="{}"/>\n'.format(uut.delay))
	    
            xml.write("        <info>\n")        
            xml.write("            <host>{}</host>\n".format(uut.epics_hn))
            
            for key, value in xml_sequence(uut):
                xml.write("            <{}>{}</{}>\n".format(key, value, key))
                            
            xml.write("        </info>\n")
            xml.write("    </record>\n")
            uut.delay += 1
            if uut.delay > 60:
                uuts.remove(uut)
            
        xml.write("</body>\n")

    try:        
	os.rename(DATFTMP, DATFILE)
    except OSError:
	print("OSError")

    time.sleep(0.5)



    
    

    
    
