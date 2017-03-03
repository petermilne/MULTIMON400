
# site customization for multimon
import threading
import time


def tty_mon(uuts):
    while True:
        for uut in uuts:            
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