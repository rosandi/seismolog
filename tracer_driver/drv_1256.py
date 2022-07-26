#!/usr/bin/python3

#---------------------------------
# ADS1256 Interface module
#
# (c) 2021, Rosandi 
#
# ADS1256 24 bit ADC differential input
# on Raspberry Pi
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

adcfac=float(0x7fffff)

class adcdriver:

    def __init__(self,port='',cmd='',verbose=True,log=None): # compatibility arguments

        self.verbose=verbose
        self.interupt=False

        if log == None:
            self.log=self._log
        else:
            self.log=log
       
        self.info={
            'ref_volt':1,
            'adc_res':1,
            'oversample':1,
            'sample_delay':0,
            'gain':[0,0,0],
            'gain_map':[1,2,4,8,16,32,64],
            'channels':3,
            'volt_scale':1/50.0,
            'active_channels':[0,1,2],
            'rate': DRATE_E['500SPS'],
            'trigger_pin': 4,
        }
        
        for c in cmd:
            self.command(c)

        self.adc=ADS1256()
        self.adc.initADC(self.info['gain'][0],self.info['rate'])
        self.adc.setMode(1) # differential input
 
        self.presample=0      # controlled by command
        self.max_fetch=100    # controlled by command
        self.channel_offset=[0,0,0]
        # GPIO.setmode(GPIO.BCM) --> set by ADS1256
        GPIO.setup(self.info['trigger_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.trigger_thread=None
        self.on_trigger=False
        self.trigger_time=0
        self.preSampleADC(self.presample)


    def _log(self, msg):
        print(msg)
 
    def preSampleADC(self, n):
        self.presample=n
        for i in range(self.presample):
            self.adc.getValue(0)
            self.adc.getValue(1)
            self.adc.getValue(2)
    
    def measure(self):
        '''
        returns a list of channel values
        '''

        nchan=self.info['channels']
        d=[0]*nchan

        for ov in range(self.info['oversample']):
            for chn in range(nchan):
                # negative number conversion
                d[chn]+=self.adc.getValue(chn)/adcfac

        for chn in range(nchan):
            d[chn]=d[chn]/self.info['oversample']

        return d

    def command(self, cmd, wait=False):
        if cmd.find('presample') == 0:
            self.presample=int(cmd.split()[1])
            self.preSampleADC()
        elif cmd.find('fmax') == 0:
            self.info['max_fetch']=int(cmd.split()[1])
        elif cmd.find('avg') == 0:
            self.info['oversample']=int(cmd.split()[1])
        elif cmd.find('dt') == 0:
            self.info['sample_delay']=int(cmd.split()[1])
        elif cmd.find('gain') == 0:
            self.info['gain']=int(cmd.split()[1])
            if adc.is_init:
                adc.configADC(self.info['gain'][0], self.info['rate'])
        elif cmd.find('info') == 0:
            for key in info:
                log(f'{key}: {info["key"]}')

    # TODO: not yet compatible with tracer

    def fetch(self):
        '''
        fetch one data from data_queue
        '''
        retv=[]
        for i in range(self.max_fetch):
            if self.qsera.empty():
                break
            else:
                retv.append(self.qsera.get())

        return retv

    def stream(self,stat=True):
        if stat:
            self.wait.clear()
        else:
            self.wait.set()

    def wait_trigger(self):
        tcancel=False

        while GPIO.input(self.info['trigger_pin']) == GPIO.HIGH:
            # to cancel: command('Q')
            if not self.wait.is_set():
                tcancel=True
                break
        
        if not tcancel:
            self.trigger_time=time() 
        
        self.wait.reset()

    def get_trigger_time(self):
        tt=self.trigger_time
        self.trigger_time=0
        return tt

    def trigger(self):
        self.clear_que()
        self.trigger_time=0
        self.on_trigger=True
        self.stream(False)
        self.trigger_thread=Thread(target=self.wait_trigger)
        self.trigger_thread.start()

    def calibrate(self):
        self.adc.calibrate()

    def updateInfo(self):
        pass

    def close(self):
        print('closing device')
        self.adc.sleep()

    def logone(self, dur, fout):
        self.interupt=False
        tt=0
        t=[]
        v=[]
        ts=time()

        if fout:
          fout=open(fname,'w')

        while tt < dur:
            
            if self.interupt:
                return

            t.append(tt)
            v.append(self.measure())
            tt=time()-ts

        if fout:
            v=np.array(v).transpose()

            jdat={
                'tsample':tt,
                'tstart':ts,
                'lon': lon,
                'lat': lat,
                'time':t, 
                'channel-00':v[0].tolist(),
                'channel-01':v[1].tolist(),
                'channel-02':v[2].tolist()
            }

            json.dump(jdat,fout)
            fout.close()

        else:
            for d in zip(t,v):
                print(d)
            print('acquisition time:', ts)

### MAIN PROGRAM ####

if __name__ == "__main__":
    
    datalog=None
    avg=10
    dt=1
    ndata=50
    nrepeat=0
    lon=-6.905977
    lat=107.613144

    for arg in sys.argv:
        if arg.find('lon=') == 0:
            lon=float(arg.replace('lon=',''))
        if arg.find('lat') == 0:
            lat=float(arg.replace('lat=',''))
        
    adc=adcdriver()
    while True:
        try:
            cmdln=input('SeismoLog_ADS1256> ')
            
            if cmdln.find('r') == 0: # record
                s=cmdln.split()
                dur=float(s[1])
                
                if dur <= 0.0:
                    continue

                if len(s) == 3:
                    adc.logone(dur,s[2])
                else:
                    adc.logone(dur, False)

            elif cmdln.find('m') == 0:
                s=cmdln.split()
                if len(s) == 1: 
                    print('required: number of data')
                    continue

                n=int(s[1])
                v=[]

                ts=time()
                for i in range(n):
                    v.append(adc.measure())
                ts=time()-ts
                
                for i in range(len(v)):
                    print('%0.5d:'%i,v[i])

                print('acquisition time:', ts)

            elif cmdln.find('q') == 0:
                adc.close()
                break

            else:
                adc.command(cmdln)
                sleep(2)
                print(ss.replace('\n','').replace(';','\n'))
                   
        except KeyboardInterrupt:
            print('terminating')
            break
            
        except Exception as e:
            print(e)
            raise

