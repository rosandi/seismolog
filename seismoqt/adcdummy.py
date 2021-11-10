#!/usr/bin/python3

#---------------------------------
# ADS1256 Interface module
#
# (c) 2021, Rosandi 
#
# ADS1256 24 bit ADC differential input
#
# rosandi@geophys.unpad.ac.id
#

from time import time,sleep,strftime
import sys
from threading import Thread,Event,Timer
from queue import Queue

chn=7
devgain=6
devchan=3
adc=None
trigpin=None

logON=Event() # initiate: clear
daemonRun=Event()
logBusy=Event()

messages={
  0: 'idle',
  1: 'acquisition',
  2: 'presample',
  3: 'initialization',
  'text': 'none'
}

tstart=0
tend=0
statid=0
logscr=True
lognum=0

def channelnum(cmask=None,nchannel=None):
    return 3, [0,1,2]

def deviceInit():
    pass    

def readadc(ts, oversample=1, delay=0.0, presample=0):
    return 0,0,0

def deviceClose():
    pass

###### MAIN PROGRAM: LOGGING ######

def logone(cfg, filename=None):
    pass

def start(cfg):
    deviceInit()
    twait=cfg['every']
    print('starting log daemon')
    
    # FIXME! this makes CPU too busy doing nothing
    while not daemonRun.isSet():
        startlog = logON.wait()        
        if daemonRun.isSet():
            break
            
        print('logging starts')
        t=time()+twait
        logone(cfg)
        logON.clear()
        
        # untested. maybe need to be canceled on quit
        Timer(twait, lambda: logON.set()).start()

    print('stopping log daemon')
    deviceClose()

