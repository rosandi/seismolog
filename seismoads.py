#!/usr/bin/python3

import time
import Adafruit_ADS1x15
from gpiozero import Button

chn=15 # channel mask! not number
gain=16
devchan=4
adc=None
trigpin=None

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

def deviceInit(port='ADS1115',speed=None):
    global adc,trigpin
    
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
            vals.append(adc.read_adc(ch,gain=gain))
            time.sleep(delay)
            
    tend=time.time()

    return tend-tstart,vals

def deviceCommand(scmd):
    global chn
    
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
   
    from time import sleep, time
    import sys
    import signal as sg
    
    blocklen=1024
    nb=None   
    filename=None
    
    sg.signal(sg.SIGINT, termhandle)
    
    for arg in sys.argv:
        if arg.find('block=') == 0:
            blocklen=int(arg.replace('block=',''))
            print('block length: %d'%(blocklen), file=sys.stderr)
        if arg.find('file=' == 0:
            filename=arg.replace('file=','')

    deviceInit()
    
    tstart=time()
    chn=1+2+4
    t,d=readadc(blocklen,chn)
    d=np.array(d).reshape((4,blocklen),order='F')
    dat={'tsample':t, 'tstart':tstart, 'x':d[0], 'y':d[1], 'z':d[2]}
    if filename is None:
        json.dump(dat)
    else:
        with open(filename, 'w') as f:
            json.dump(dat,f)
    
    deviceClose()
