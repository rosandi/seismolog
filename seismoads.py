#!/usr/bin/python3

import time
import Adafruit_ADS1x15
from gpiozero import Button

chn=15 # channel mask! not number
gain=16
devchan=4
adc=None
trigpin=None
rate=None

def channelnum(cmask=None,nchannel=None):
    global chn
    maxc=devchan
    if cmask is None:
        cmask=chn
    if nchannel:
        maxc=nchannel
    chlst=[] # array index list! not mask!
    nch=0
    li=0 # list index
    for m in range(maxc):
        pm=2**m
        if cmask & pm:
            chlst.append(li)
            nch+=1
        li+=1

    return nch,chlst

def deviceInit(port='ADS1115',speed=860):
    global adc,trigpin,rate
    
    rate=speed
    trigpin=Button(4)
    
    if port == 'ADS1115':
        adc = Adafruit_ADS1x15.ADS1115()
    elif port == 'ADS1015':
        adc = Adafruit_ADS1x15.ADS1015()
    else:
        print('unknown device: {}'.format(port))
        exit()

def readadc(n=1,channels=None, delay=0.0):
    global gain
    _,cl=channelnum(channels)
    vals=[]
    tstart=time.time()
    for i in range(n):
        for ch in cl:
            vals.append(adc.read_adc(ch,gain=gain,data_rate=rate))
            time.sleep(delay)
            
    tend=time.time()

    return tend-tstart,vals

def deviceCommand(scmd):
    global chn,gain
    
    nchan,chlist=channelnum(chn)
    
    if scmd.find('msr')==0:
        ndata=int(scmd.split()[1])
        dt,vals=readadc(ndata)
        return dt, vals

    elif scmd.find('trig')==0:
        trigpin.wait_for_press()
        dt,vals=readadc(ndata)
        return dt, vals
        
    elif scmd.find('chn')==0:
        chn=int(scmd.split()[1])
        nchan,_=channelnum(chn)
        return "channel mask: {} number {}".format(chn,nchan)
    
    elif scmd.find('gain')==0:
        gain=int(scmd.split()[1])
        return "gain %d"%(gain)

    else:
        return "ADS1x15 interface"
    
def directMeasure(n=1):
    return readadc(n)
    
def clearQueue():
    pass

def deviceClose():
    pass

###### MAIN PROGRAM: LOGGING ######

if __name__ == "__main__":
   
    import sys
    import json
    import numpy as np
    
    blocklen=100
    dly=0
    avg=1 # oversampling average
    
    filename=time.strftime('%Y%m%d%H%M%S')+'.json'
    
    for arg in sys.argv:
        if arg.find('block=') == 0:
            blocklen=int(arg.replace('block=',''))
            print('block length: %d'%(blocklen), file=sys.stderr)
        if arg.find('file=') == 0:
            filename=arg.replace('file=','')
        if arg.find('gain=') == 0:
            gain=int(arg.replace('gain=',''))
        if arg.find('chanmask=') == 0:
            chn=int(arg.replace('chanmask=',''))
        if arg.find('delay=') == 0:
            dly=float(arg.replace('delay=',''))
        if arg.find('avg=') == 0:
            avg=int(arg.replace('avg=',''))

    deviceInit()
    
    tstart=time.time()

    chn=1+2+4
    ad=np.zeros(blocklen*3)
    for a in range(avg):
        t,d=readadc(blocklen,chn,dly)
        ad+=np.array(d)
    
    ad=(ad/avg).reshape((3,blocklen),order='F')
    d=ad.tolist()
    
    dat={
        'tsample':t, 'tstart':tstart, 'length': blocklen, 
        'x':d[0], 'y':d[1], 'z':d[2]
        }
    
    f=open(filename, 'w')
    json.dump(dat,f)
    f.close()
    
    deviceClose()
