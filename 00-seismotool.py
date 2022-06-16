import numpy as np
from scipy.fftpack import fft
from scipy.signal import butter,filtfilt
import matplotlib.pyplot as plt
import json

print('\n*** SEISMO-LOG ***')
print('''Commands:
loadjson(file) 

plotjson(file,domain=domain,field='xyz',smooth=strength,log=True|False) 
  # domain= 'time','freq','hvsr'

plothvsr(files,smooth=strength)
''')

def loadjson(fname):
    with open(fname) as f:
        d=json.load(f)
    return d

def plotjson(fname, domain='time', field='xyz', smooth=None, log=False, show=True):
    d=loadjson(fname)
    x=d['data'][0]
    y=d['data'][1]
    z=d['data'][2]
    dt=d['tsample']/d['length']
    
    if smooth !=None:
        butta,buttb = butter(4, smooth, btype='low', analog=False)
        
    if domain=='freq':
        m=int(len(x)/2)
        fmax=1/dt
        f=np.linspace(0,fmax,d['length'])

        if field.find('x')>=0:
            x=np.abs(fft(x))
            x[0]=0
            if smooth!=None:
                x=filtfilt(butta,buttb,x)
            plt.plot(f[:m],x[:m])
        if field.find('y')>=0:
            y=np.abs(fft(y))
            y[0]=0
            if smooth!=None:
                y=filtfilt(butta,buttb,y)
            plt.plot(f[:m],y[:m])
        if field.find('z')>=0:
            z=np.abs(fft(z))
            z[0]=0
            if smooth!=None:
                z=filtfilt(butta,buttb,z)
            plt.plot(f[:m],z[:m])
        
        plt.xlabel('Hz')
        plt.ylabel('mag. (arb.)')
                
    elif domain=='hvsr':
        m=int(len(x)/2)
        fmax=1/dt
        f=np.linspace(0,fmax,d['length'])
        x=fft(x)
        y=fft(y)
        z=fft(z)
        h=np.abs(np.sqrt(x*x+y*y)/np.sqrt(z*z))
        if smooth != None:
            hf=filtfilt(butta, buttb, h)
            plt.plot(f[:m],hf[:m])
        else:
            plt.plot(f[:m],h[:m])
        plt.xlabel('Hz')
        plt.ylabel('mag. (arb.)')
        
    else:
        t=np.linspace(0,d['tsample'],d['length'])
        
        if smooth != None:
            x=filtfilt(butta,buttb,x)
            y=filtfilt(butta,buttb,y)
            z=filtfilt(butta,buttb,z)
            
        if field.find('x')>=0:
            plt.plot(t,x)
        if field.find('y')>=0:
            plt.plot(t,y)
        if field.find('z')>=0:
            plt.plot(t,z)
        
        plt.xlabel('second')
        plt.ylabel('ampl. (Vmax)')


    if log:
        plt.semilogx()
    
    if show:
        plt.show()


def plothvsr(fname,smooth=0.1,log=True,show=True):
    if isinstance(fname,list):
        for nm in fname:
            plotjson(nm,domain='hvsr', smooth=smooth, log=log, show=False)
        plt.show()
    else:
        plotjson(fname,domain='hvsr', smooth=smooth, log=log)
