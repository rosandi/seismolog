#!/usr/bin/python3
# -*- coding:utf-8 -*-


import time
import ADS1256
import RPi.GPIO as GPIO
import sys

N=50
vgain=0
chan='xyz'

for arg in sys.argv:
    arg=arg.strip()

    if arg.find('n=') == 0:
        N=int(arg.replace('n=',''))
    if arg.find('ch=') == 0:
        chan=arg.replace('ch=','')
    if arg.find('g=') == 0:
        vgain=int(arg.replace('g=',''))

if vgain > 6:
    vgain=0

ADC = ADS1256.ADS1256()
ADC.ADS1256_init()
ADC.ADS1256_SetMode(1)
ADC.ADS1256_ConfigADC(vgain,0x82)

vx=0
vy=0
vz=0

for i in range(10):
    ADC.ADS1256_GetChannalValue(0)
    ADC.ADS1256_GetChannalValue(1)
    ADC.ADS1256_GetChannalValue(2)

#time.sleep(1)

for i in range(N):
    if chan.find('x')>=0:
        vx = ADC.ADS1256_GetChannalValue(0)/float(0x7fffff)
    if chan.find('y')>=0:
        vy = ADC.ADS1256_GetChannalValue(1)/float(0x7fffff)
    if chan.find('z')>=0:
        vz = ADC.ADS1256_GetChannalValue(2)/float(0x7fffff)

    print ("%f %f %f"%(vx,vy,vz))
    

GPIO.cleanup()
print ("#Program end     ")


