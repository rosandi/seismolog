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
import ADS1256
import RPi.GPIO as GPIO

chn=7 # channel mask! not number
gain='ADS1256_GAIN_16'
devchan=3
adc=None
trigpin=None
rate='ADS1256_50SPS'

def channelnum(cmask=None,nchannel=None):
    return 3, [0,1,2]

def deviceInit():
	global gain, adc
    adc=ADS1256.ADS1256()
    adc.ADS1256_init()
    adc.ADS1256_ConfigADC(gain,rate)
    adc.ADS1256_SetMode(1) # differential input

def readadc(n=1, oversample=1, delay=0.0):
	vals=[]
	tstart=time.time()
	
	for i in range(n):	
		x=0
		y=0
		z=0
		
		for i in range(oversample):
			x+=adc.ADS1256_GetChannalValue(0)
			y+=adc.ADS1256_GetChannalValue(1)
			z+=adc.ADS1256_GetChannalValue(2)
		
		vals.append(x/oversample)
		vals.append(y/oversample)
		vals.append(z/oversample)
		
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
    
    elif scmd.find('gain')==0:
        gain=int(scmd.split()[1])
        return "gain %d"%(gain)

    else:
        return "ADS1256 interface"
    
def directMeasure(n=1):
    return readadc(n)
    
def clearQueue():
    pass

def deviceClose():
	adc.ADS1256_sleep()
    pass

###### MAIN PROGRAM: LOGGING ######

if __name__ == "__main__":
   
    import sys
    import json
    import numpy as np
    
    from sensors import pvsense   
    
    blocklen=100
    dly=0
    avg=1 # oversampling average
    datapath='.'
    sensors='all'
    filename=None
    
    for arg in sys.argv:
        if arg.find('block=') == 0:
            blocklen=int(arg.replace('block=',''))
            print('block length: %d'%(blocklen), file=sys.stderr)
        if arg.find('file=') == 0:
            filename=arg.replace('file=','')
        if arg.find('gain=') == 0: # accept only string
            gain=arg.replace('gain=','')
        if arg.find('delay=') == 0:
            dly=float(arg.replace('delay=',''))
        if arg.find('avg=') == 0: # oversampling
            avg=int(arg.replace('avg=',''))
        if arg.find('dir=') == 0:
            datapath=arg.replace('dir=','')
        else:
			print('unimplemented parameter: ',arg)
    
    if filename==None:
    	filename=datapath+'/'+time.strftime('%Y%m%d%H%M%S')+'.json'
    
    deviceInit()
    ad=np.zeros(blocklen*3)  
    tstart=time.time()
    t,d=readadc(blocklen,avg,dly)
    ad=np.array(d).reshape((3,blocklen),order='F')
    d=ad.tolist()

    dat={
        'tsample':t, 'tstart':tstart, 'length': blocklen, 
        'x':d[0], 'y':d[1], 'z':d[2]
        }
        
    f=open(filename, 'w')
    json.dump(dat,f)
    f.close()
    
    deviceClose()
