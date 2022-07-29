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
from trigger import triggerIO

# true value: v_ref*val/adcfac/gain

adcfac=float(0x7fffff)

class adcdriver:

    def __init__(self,port='',cmd='',verbose=True,log=None): # compatibility arguments

        self.verbose=verbose

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
            'rate': DRATE_E['500SPS']
        }
        
        for c in cmd:
            self.command(c)

        self.adc=ADS1256()
        self.adc.initADC(self.info['gain'][0],self.info['rate'])
        self.adc.setMode(1) # differential input
 
        self.presample=0      # controlled by command
        self.max_fetch=100    # controlled by command
        self.channel_offset=[0,0,0]
        self.trigger_time=0
        self.preSampleADC(self.presample)
        self.que=None
        self.trg=triggerIO

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
        d=[0.0]*nchan

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
    
    def read_stream(self):
        ts=time()
        while not self.trd_intr.is_set():
            tt=time()-ts
            d=self.measure()
            self.que.put((tt,d))

    def fetch(self):
        retv=[]
        for i in range(self.max_fetch):
            if self.que.empty():
                break
            else:
                retv.append(self.que.get())

        return retv

    def stream(self,stat=True):
        
        if stat:
            self.que=Queue
            self.trd_intr.clear()
            self.trd=Thread(target=self.read_stream)
            self.trd.start()
        else:
            if self.que:
                self.trd_intr.set()
                self.trd.join()
                self.que=None

    def trigger(self):
        self.trg.wait(self.stream)

    def get_trigger_time(self):
        return self.trg.get_trigger_time()

    def calibrate(self):
        self.adc.calibrate()

    def updateInfo(self):
        pass

    def close(self):
        print('closing device')
        self.stream(False)
        self.adc.sleep()

### MAIN PROGRAM ####

if __name__ == "__main__":
    
    datalog=None
    avg=10
    dt=1
    ndata=50
    nrepeat=0

#    for arg in sys.argv:
#        if arg.find('comm=') == 0:
#            comm=arg.replace('comm=','')
#        if arg.find('speed=') == 0:
#            speed=int(arg.replace('speed=',''))

    adc=adcdriver()
    while True:
        try:
            cmdln=input('SeismoLog_ADS1256> ')
            
            if cmdln.find('r') == 0: # record
                s=cmdln.split()
                dur=float(s[1])
                
                if not dur:
                    continue

                if len(s) == 3:
                    fout=open(s[2],'w')
                else:
                    fout=None

                ts=time()
                tt=time()

                t=[]
                v=[]

                while tt-ts < dur:
                    tt=time()
                    t.append(tt)
                    v.append(adc.measure())

                ts=tt-ts

                if fout:
                    v=np.array(v).transpose()

                    jdat={
                            'time':t, 
                            'channel-00':v[0].tolist(),
                            'channel-01':v[1].tolist(),
                            'channel-02':v[2].tolist(),
                            'tsample':ts
                        }

                    json.dump(jdat,fout)
                    fout.close()

                else:
                    for d in zip(t,v):
                        print(d)
                    print('acquisition time:', ts)

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

