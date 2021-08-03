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

import time
from ADS1256 import ADS1256, DRATE_E
import RPi.GPIO as GPIO

chn=7 # channel mask! not number
devgain=4
devchan=3
adc=None
trigpin=None
rate=DRATE_E['1000SPS']

def channelnum(cmask=None,nchannel=None):
    return 3, [0,1,2]

def deviceInit():
    global devgain, adc
    adc=ADS1256()
    adc.initADC(devgain,rate)
    adc.setMode(1) # differential input

def readadc(n=1, oversample=1, delay=0.0, presample=0):
    vals=[]
    tstart=time.time()
    
    # presampling: throw out bad data
    for i in range(presample):
        adc.getValue(0)
        adc.getValue(1)
        adc.getValue(2)
    
    for i in range(n):	
        x=0
        y=0
        z=0

        for i in range(oversample):
            x+=adc.getValue(0)
            y+=adc.getValue(1)
            z+=adc.getValue(2)

        vals.append(x/oversample/float(0x7fffff))
        vals.append(y/oversample/float(0x7fffff))
        vals.append(z/oversample/float(0x7fffff))
        
        if delay>0: # faster, maybe...
            time.sleep(delay)

    tend=time.time()
    return tend-tstart,vals
    
def readadc_t(ts, oversample=1, delay=0.0, presample=0):
    
    vals=[]
    tstart=time.time()
    tend=tstart+ts;
    
    # presampling: throw out bad data
    for i in range(presample):
        adc.getValue(0)
        adc.getValue(1)
        adc.getValue(2)
    
    while(time.time() < tend):
        x=0
        y=0
        z=0

        for i in range(oversample):
            x+=adc.getValue(0)
            y+=adc.getValue(1)
            z+=adc.getValue(2)

        vals.append(x/oversample/float(0x7fffff))
        vals.append(y/oversample/float(0x7fffff))
        vals.append(z/oversample/float(0x7fffff))

        if delay>0: # faster, maybe...
            time.sleep(delay)
        
    tend=time.time()
    return tend-tstart,vals

def deviceCommand(scmd):
    global chn,devgain
    
    nchan,chlist=channelnum(chn)
    
    if scmd.find('msr')==0:
        ndata=int(scmd.split()[1])
        dt,vals=readadc(ndata)
        return dt, vals
    
    elif scmd.find('gain')==0:
        devgain=int(scmd.split()[1])
        return "gain %d"%(devgain)

    else:
        return "ADS1256 interface"
    
def directMeasure(n=1):
    return readadc(n)
    
def calibrate():
    adc.calibrate()
    
def clearQueue():
    pass

def deviceClose():
    adc.sleep()

###### MAIN PROGRAM: LOGGING ######

if __name__ == "__main__":
   
    import sys
    import json
    import numpy as np
    
    blocklen=100 # deprecated: use stime
    dly=0
    avg=1 # oversampling average
    datapath='.'
    sensors='all'
    filename=None
    fileformat='json'
    major='column'
    presample=0
    sampletime=0
    
    for arg in sys.argv:
        arg=arg.strip()

        if arg.find('block=') == 0:
            blocklen=int(arg.replace('block=',''))
            print('block length: %d'%(blocklen), file=sys.stderr)
        if arg.find('stime=') == 0:# sample time in second
            sampletime=int((arg.replace('stime=',''))
        if arg.find('file=') == 0:
            filename=arg.replace('file=','')
        if arg.find('gain=') == 0:
            devgain=int(arg.replace('gain=',''))
        if arg.find('dt=') == 0: # sample period (minus oversampling time)
            dly=float(arg.replace('dt=',''))
        if arg.find('avg=') == 0: # oversampling
            avg=int(arg.replace('avg=',''))
        if arg.find('dir=') == 0:
            datapath=arg.replace('dir=','')
        if arg.find('format=') == 0:
            fileformat=arg.replace('format=','')
        if arg.find('major=') == 0:
            major=arg.replace('major=','')
        if arg.find('presample=') == 0:
            presample=int(arg.replace('presample=',''))

    
    if filename==None:
        filename=datapath+'/'+time.strftime('%Y%m%d%H%M%S')
    
    deviceInit()
    ad=np.zeros(blocklen*3)  
    tstart=time.time()
    
    if(sampletime>0):
        t,d=readadc_t(sampletime,avg,dly,presample)
    else:
        t,d=readadc(blocklen,avg,dly,presample)
        
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
            'data':ad
            }
        
        filename=filename+'.json'
        f=open(filename, 'w')
        json.dump(dat,f)
        f.close()
    
    deviceClose()
