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

def directMeasure(n=1):
    return readadc(n)
    
def calibrate():
    adc.calibrate()

def deviceClose():
    deviceReady=False
    adc.sleep()

adcfac=float(0x7fffff)

class adcdriver:

    def __init__(self,port='',cmd='',verbose=True,log=None): # compatibility arguments

        self.verbose=verbose

        if log == None:
            self.log=self._log
        else:
            self.log=log

        self.qsera = Queue()
        self.ev=Event()
        self.wait=Event()
        self.ev.clear()
        self.wait.set()
       
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
        self.adc.initADC(self.info['gain'][0],rate)
        self.adc.setMode(1) # differential input
 
        self.presample=0      # controlled by command
        self.max_fetch=100    # controlled by command
        self.channel_offset=[0,0,0]
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.info['trigger_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.data_thread=Thread(target=self.read_stream)
        self.data_thread.start()
        self.trigger_thread=None
        self.on_trigger=False
        self.trigger_time=0
        self.preSampleADC(self.presample)


    def _log(self, msg):
        print(msg)
 
    def preSampleADC(self, n):
        self.presample=n
        for i in range(self.presample):
            adc.getValue(0)
            adc.getValue(1)
            adc.getValue(2)
    
    def clear_que(self):
        s=''
        while not self.qsera.empty():
            s+=self.qsera.get()[1]+'\n'
        return s

    def dump_que(self):
        s=''
        while not self.qsera.empty():
            dd=self.qsera.get()
            s.append(f"{dd[0]} {dd[1]}\n")
        return s

    def measure(self):
        '''
        returns a list of channel values
        '''

        nchan=self.info['channels']
        d=[0]*nchan

        for ov in range(self.info['oversample'])
            for chn in range(nchan):
                # negative number conversion
                d[cnh]+=adc.getValue(n)/adcfac

        for chn in range(nchan):
            d[chn]=d[chn]/self.info['oversample']

        return d
 
    def read_stream(self):

        while True:
            
            while self.wait.is_set():
                pass

            if self.on_trigger:
                self.on_trigger=False
                self.trigger_time=time()
                self.trigger_thread.join()

            self.qsera.put((time(),self.measure()))  #FIXME
            sleep(self.info['sample_delay']/1000.0)

            if self.ev.is_set():
                break
    
    def waiting(self):
        return self.wait.is_set()

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

        elif cmd == 'Q':
            self.clear_que()
            self.wait.reset()
        
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
        self.clear_que()
        self.ev.set()
        self.data_thread.join()

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
            
            if cmdln.find('quit') == 0:
                adc.close()
                break
            
            elif cmdln.find('save') == 0:
                fname=cmdln.replace('file','').strip()

                if fname != '':
                    datalog=open(fname,'w')

            elif cmdln.find('close') == 0 and datalog:
                datalog.close()
                datalog=None

            elif cmdln.find('flush') == 0:
                print(adc.clear_que())
            
            elif cmdln.find('measure') == 0:
                s=cmdln.split()
                if len(s) == 1: continue
                n=int(s[1])
                for i in range(n):
                    print(adc.measure())

            else:
                adc.command(cmdln)
                sleep(2)
                ss=adc.clear_que()
                print(ss.replace('\n','').replace(';','\n'))

                if datalog:
                    datalog.write(ss)
                   
        except KeyboardInterrupt:
            print('terminating')
                    
        except Exception as e:
            print(e)

