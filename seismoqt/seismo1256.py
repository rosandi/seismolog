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
from ADS1256 import ADS1256, DRATE_E
import RPi.GPIO as GPIO
import sys
import json
import numpy as np
from threading import Thread, Event, Timer
from queue import Queue

devgain=6
adc=None
deviceReady=False

# rate>1000SPS prone to noise!
rate=DRATE_E['500SPS']

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

def printlog(s):
    if logscr:
        print(s)
    else:
        essages['text']=s

def channelnum(cmask=None,nchannel=None):
    return 3, [0,1,2]

def deviceInit(gain,rate):
    global devgain, adc
    adc=ADS1256()
    adc.initADC(gain,rate)
    adc.setMode(1) # differential input
    deviceReady=True
    
def readadc(ts, oversample=1, delay=0.0, presample=0):
    global statid, tstart, tend
    
    vals=[]
    
    # presampling: throw out bad data
    statid=2
    for i in range(presample):
        adc.getValue(0)
        adc.getValue(1)
        adc.getValue(2)
    
    statid=1
    tstart=time()
    tend=tstart+ts;
    #cnt=0
    #print(ts,oversample,delay)
    
    while(time() < tend):
        x=0
        y=0
        z=0
        oi=0

        while oi<oversample:

            if not daemonRun.isSet():
              return 0,[0,],0

            x+=adc.getValue(0)
            y+=adc.getValue(1)
            z+=adc.getValue(2)
            oi+=1            

        vals.append(x/oversample/float(0x7fffff))
        vals.append(y/oversample/float(0x7fffff))
        vals.append(z/oversample/float(0x7fffff))

        if delay>0: # faster, maybe...
            sleep(delay)
        # cnt+=1
        
    tend=time()
    blocklen=int(len(vals)/3)
    statid=0
    #print(tend-tstart, blocklen, cnt)
    
    return tend-tstart,vals,blocklen
    
def directMeasure(n=1):
    return readadc(n)
    
def calibrate():
    adc.calibrate()

def deviceClose():
    deviceReady=False
    adc.sleep()

###### MAIN PROGRAM: LOGGING ######

def logone(cfg, filename=None):
    global lognum

    logBusy.set()
    datapath=cfg['datapath']
    major=cfg['format']
    presample=0
    sampletime=cfg['tsample']
    avg=cfg['oversample']
    dly=cfg['dt']
    lon=cfg['lon']
    lat=cfg['lat']
    fileformat='json'
    
    if datapath[len(datapath)-1] != '/':
        datapath+='/'

    if filename==None:
        filename=datapath+strftime('%Y%m%d%H%M%S')
    
    lognum+=1

    # read a block of data
    t,d,blocklen=readadc(sampletime,avg,dly,presample)
    
    if not daemonRun.isSet():
        print('logging canceled')
        logBusy.clear()
        return
    
    if fileformat == 'text':
        filename=filename+'.txt'
        f=open(filename, 'w')
        f.write('# tsample= %0.6f\n'%(t))
        f.write('# tstart= %0.6f\n'%(tstart))
        f.write('# length= %d\n'%(blocklen))
        ad=np.array(d).reshape((3,blocklen),order='F')

        for i in range(blocklen):
            f.write("%f %f %f\n"%(ad[0][i],ad[1][i],ad[2][i]))
        f.close()
        
    else:
        if major == 'column':
            ad=np.array(d).reshape((3,blocklen),order='F').tolist()
        else:
            ad=np.array(d).reshape((blocklen,3)).tolist()
        
        dat={
            'tsample':t, 
            'tstart':tstart, 
            'length': blocklen, 
            'lon': lon,
            'lat': lat,
            'data':ad
            }
        
        filename=filename+'.json'
        f=open(filename, 'w')
        json.dump(dat,f)
        f.close()
    print('written:', filename)
    logBusy.clear()

def start(cfg):

    deviceInit(cfg['gain'],rate)
    twait=cfg['every']
    print('starting log daemon')
    daemonRun.set()
    logON.set()
    sleep(10) # just wait to let things set up
    
    # FIXME! this makes CPU too busy doing nothing
    while daemonRun.isSet():
        
        startlog = logON.wait()        

        if not daemonRun.isSet():
            break
            
        print('logging starts')
        t=time()
        logone(cfg)
        t=twait-(time()-t)
        
        if t<0: t=0
        
        print('wait for %0.2f seconds'%(t))
        
        logON.clear()
        tm=Timer(twait, lambda: logON.set())
        tm.start()
    
    tm.cancel()
    deviceClose()
    print('log daemon stop')

def stop():
    logON.set() # release event wait()
    daemonRun.clear() 

if __name__ == "__main__":
    cfg = {
    'gain': 6,
    'tsample': 30,
    'dt': 0,
    'oversample': 1,
    'every': 60,
    'datapath': './',
    'format': 'column',
    'lon': 6.9175,
    'lat': 107.6191
    }
    
    outfile=None
    
    for arg in sys.argv:
        if arg.find("conf=") == 0:
            fjs=arg.replace("conf=","")
            
            try:
                print("reading configuration file:",fjs)
                with open(fjs) as f:
                    tcfg=json.load(f)
                cfg=tcfg
            except:
                print("failed opening config file")
                
        if arg.find("out=") == 0:
            outfile=arg.replace("out=","")
    
    deviceInit(cfg['gain'],rate)
    daemonRun.set()
    logone(cfg,outfile)
    deviceClose()
