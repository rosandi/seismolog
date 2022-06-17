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

    def __init__(self,port,cmd):

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
    
    def read_stream(self):

        while True:
            
            while self.wait.is_set():
                pass

            n=self.info['channels']
            d=[0]*n
            
            for ov in range(self.info['oversample'])
                for chn in range(n):
                    d[cnh]+=adc.getValue(n)/adcfac

            for chn in range(n):
                d[chn]/=adcfac
            
            sleep(self.info['sample_delay']/1000.0)
            self.qsera.put((time(),','.join(data)))

            if self.ev.is_set():
                break

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

    def preSampleADC(self, n):
        self.presample=n
        for i in range(self.presample):
            adc.getValue(0)
            adc.getValue(1)
            adc.getValue(2)
 
    def command(self, cmd, wait=False):
        if cmd.find('presample'):
            self.presample=int(cmd.split()[1])
        elif cmd.find('fmax'):
            self.info['max_fetch']=int(cmd.split()[1])
        elif cmd.find('avg'):
            self.info['oversample']=int(cmd.split()[1])
        elif cmd.find('dt'):
            self.info['sample_delay']=int(cmd.split()[1])
        elif cmd.find('gain'):
            self.info['gain']=int(cmd.split()[1])
            if adc.is_init:
                adc.configADC(self.info['gain'][0], self.info['rate'])
        
    def calibrate(self):
        self.adc.calibrate()

    def stream(self,stat):
        if self.presample:
            self.preSampleADC(self.presample)

        if stat:
            self.wait.clear()
        else:
            self.wait.set()

    def wait_trigger(self):
        
        while GPIO.input(self.info['trigger_pin']) == GPIO.HIGH:
            pass
        
        self.wait.reset()

    def trigger(self):
        self.clear_que()
        self.stream(False)
        self.trigger_thread=Thread(target=self.wait_trigger)

    # TODO: not yet compatible with seiplot

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

    def updateInfo(self):
        pass

    def close(self):
        self.clear_que()
        self.ev.set()
        self.data_thread.join()

