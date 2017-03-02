# multimon400
## web based system monitor for acq400 series.

## Theory of operation
1. multimon400.py is a monitor process runs on the webserver
  1. spawns casw to monitor EPICS beacons
  2. for each EPICS IOC, spawns a monitor for notable PV's
  3. the monitors collect PV data
  4. a polling thread stores the data to multimon_acq400.xml
2. web clients load multimon_acq400.html
  1. a JS poll loop fetches multimon_acq400.xml
  2. the web page renders the data with the transform in multimon_acq400.xsl

A more modern implementation would probably use a json data file and a pure .js render script ..

## Prerequisites

### EPICS BASE
#### http://www.aps.anl.gov/epics
#### http://cars9.uchicago.edu/software/python/pyepics3/
1. http://www.aps.anl.gov/epics/base/R3-14/12.php download sources
2. Build in eg /home/epics/
3. cd /home/epics/; wget https://www.aps.anl.gov/epics/download/base/baseR3.14.12.6.tar.gz
4. tar xvzd *tar.gz
5. cd base*
5.5 you'll need gcc, g++, readline-devel
6. export EPICS_HOST_ARCH=$(./startup/EpicsHostArch)
7. make
8. create this shell profile:

[peter@eigg base-3.14.12.6]$ cat /etc/profile.d/epics.sh   
export EPICS_BASE=/home/epics/base-3.14.12.6
export PATH=$PATH:$EPICS_BASE/bin/linux-x86_64  
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$EPICS_BASE/lib/linux-x86_64  

### PYTHON
1. pip install pyepics



