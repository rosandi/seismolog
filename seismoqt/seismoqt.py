#!/usr/bin/python3

#---------------------------------
# Seismo-Log QT Application
#
# (c) 2021, Rosandi 
#
# ADS1256 24 bit ADC differential input
#
# rosandi@geophys.unpad.ac.id
#

import os
import sys
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer, QUrl
from style import style as css
from plotter import plotter
import json
from datetime import datetime
from threading import Thread,Event
from queue import Queue
from PyQt5.QtWebKitWidgets import QWebView

winmode='max'
winx=1024
winy=600
configfile='/home/seismo/config.json'
docfile='file:///home/seismo/doc/about-id.html'
dummy=False
dpath=None
stayon=False

for arg in sys.argv:
    if arg.find('mode=') == 0:
        winmode=arg.replace('mode=','')
    if arg.find('dummy=') == 0:
        if arg.replace('dummy=','') == 'true':
            dummy=True
    if arg.find('config=') == 0:
        configfile=arg.replace('config=','')
    if arg.find('doc=') == 0:
        docfile=arg.replace('doc=','')
    if arg.find('dpath=') == 0:
        dpath=arg.replace('dpath=','')
    if arg.find('shutdown=') == 0:
        if arg.replace('shutdown=','') == 'no':
            stayon=True

if dummy:
    import adcdummy as adc
else:
    import seismo1256 as adc

try:
    fl=open(configfile)
    adc_settings=json.load(fl)
    fl.close()
except: # default
    print('using default configuration')
    adc_settings = {
        'gain': 6,
        'tsample': 30,
        'dt': 0,
        'oversample': 1,
        'every': 0,
        'datapath': '/home/seismo/data/',
        'format': 'column'
    }

if dpath != None:
    adc_settings['datapath'] = dpath

class tabButton(QPushButton):
    def __init__(self, master, text, pos, act=None):
        super(tabButton,self).__init__(text,master)
        self.resize(200, 80)
        self.move(pos[0], pos[1])
        self.setStyleSheet(css['button'])

        if (act != None):
            self.clicked.connect(act)
        
class cmdButton(QPushButton):
    def __init__(self,master,text,pos,sz,act=None):
        super(cmdButton,self).__init__(text,master)
        self.resize(sz[0],sz[1])
        self.move(pos[0],pos[1])
        self.setObjectName('cmdButton')
        self.setStyleSheet(css['button'])
        if (act != None):
            self.clicked.connect(act)

class statusText(QTextEdit):
    def __init__(self, master, pos, sz):
        super(statusText, self).__init__(master)
        self.move(pos[0],pos[1])
        self.resize(sz[0],sz[1])
        self.setStyleSheet(css['text'])

        
class scroller(QScrollBar):
    def __init__(self, master, geo, lim=(0,100,1), proc=None):
        super(scroller,self).__init__(Qt.Horizontal,master)
        self.resize(geo[2],geo[3])
        self.move(geo[0],geo[1])
        self.setStyleSheet(css['main'])
        self.setMinimum(lim[0])
        self.setMaximum(lim[1])
        self.setSingleStep(lim[2])
        if proc != None:
            self.valueChanged.connect(proc)
        
class dataList(QListWidget):
    
    def __init__(self, master, geo, datapath):
        super(dataList,self).__init__(master)
        self.master=master
        self.datapath=datapath
        self.resize(geo[2],geo[3])
        self.move(geo[0],geo[1])
        self.itemClicked.connect(self.plot)
        self.setStyleSheet(css['main'])
        self.verticalScrollBar().setStyleSheet('width: 30px;')
            
    def plot(self, item):
        self.master.plot(self.datapath+item.text()+'.json')
        
    def update(self):
        ext='.json'
        datafiles=[]
        for df in os.listdir(self.datapath):
            if df.find(ext,len(df)-5) > 0:
                datafiles.append(df)
                
        cnt=len(datafiles)
        datafiles.sort(reverse=True)
        
        self.clear()
        
        for d in datafiles:
            self.addItem(d.replace('.json',''))
        
        
class label(QLabel):
    def __init__(self,master,text,pos):
        super(label, self).__init__(master)
        self.setText(text)
        self.move(pos[0],pos[1])
        self.setStyleSheet(css['label'])
        if len(pos)>2:
            self.resize(pos[2],pos[3])
   

#### TABS #####

class controlTab(QFrame):
    def __init__(self, master, pos):
        super(controlTab, self).__init__(master)
        self.master=master
        self.move(pos[0],pos[1])
        self.resize(winx-220,600)
        self.setStyleSheet('background-color: gray;')
        self.create()
    
    def status(self):
        s=self.devstat.toPlainText()
        if adc.logON.isSet():
            s+='logging active\n'
        else:
            s+='logging stopped\n'
        
        self.devstat.setText(s)
    
    def startLog(self):
        if not adc.daemonRun.isSet():
            self.master.startLogThread()
            s=self.devstat.toPlainText()
            s+='start logging at '+datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+'\n'
            self.devstat.setText(s)
            self.startBtn.setText('STOP')
            self.startBtn.setStyleSheet(css['actbutton'])
        else:
            self.master.stopLogThread()
            s=self.devstat.toPlainText()
            s+='stop logging at '+datetime.now().strftime("%m/%d/%Y, %H:%M:%S")+'\n'
            self.devstat.setText(s)
            self.startBtn.setText('START')
            self.startBtn.setStyleSheet(css['cmdbutton'])
            
    def device_shutdown(self):
        self.devstat.setText(' Going down\n GOOD BYE')
        QTimer().singleShot(5000, lambda: seismoGUI.close())
            
    def create(self):
        self.devstat=statusText(self, [10,100], [760,400])
        self.statusBtn=cmdButton(self,'STATUS', (20,10), (150,60), self.status)
        self.startBtn=cmdButton(self,'START', (200,10), (150,60), self.startLog)
        self.clearBtn=cmdButton(self,'CLEAR', (20,510), (150,60), lambda: self.devstat.setText(''))
        self.pdownBtn=cmdButton(self,'SHUTDOWN', (520,510), (220,60), self.device_shutdown)
        
        self.clearBtn.setStyleSheet(css['button']);
        self.pdownBtn.setStyleSheet(css['warnbutton']);

class dataTab(QFrame):
    def __init__(self, master, pos):
        super(dataTab, self).__init__(master)
        self.move(pos[0],pos[1])
        self.resize(winx-220,600)
        self.setStyleSheet('background-color: green;')
        #self.setObjectName('dataTab')
        #self.setStyleSheet(css['main'])
        
        self.create()

    def update_to(self):
        if self.isHidden():
            self.ticks.stop()
        else:
            self.datalist.update()
            
    def create(self):
        label(self,'FILE LIST', (620,5,200,30))
        self.plotx=plotter(self, [10, 10, 540, 180])        
        self.ploty=plotter(self, [10, 200, 540, 180])        
        self.plotz=plotter(self, [10, 390, 540, 180])
        self.datalist=dataList(self, [560, 30, 245,400], adc_settings['datapath'])
        self.dinfo=statusText(self, [560,440], [235,130])
        self.lxmin=label(self, '0', (20, 570, 160, 20))
        self.lxmax=label(self, '1s', (530, 570, 160, 20))
        self.lxmax.setStyleSheet('color: white;')
        self.lxmin.setStyleSheet('color: white;')
        self.ticks=QTimer()
        self.ticks.timeout.connect(lambda: self.update_to())
        
    def plot(self, dname):    
        
        with open(dname) as f:
            d=json.load(f)
        
        self.plotx.plot(d['data'][0])
        self.ploty.plot(d['data'][1])
        self.plotz.plot(d['data'][2])
        logtime=datetime.fromtimestamp(d['tstart']).strftime("%m/%d/%Y %H:%M:%S")
        dinfo=self.dinfo
        nn=dname.split('/')
        nn=nn[len(nn)-1].replace('.json','')
        dinfo.setText(nn+'\n\n'+logtime+'\ntsample:%0.5e\nlength:%d'%(d['tsample'],d['length']))
        self.lxmax.setText('%0.1fs'%(d['tsample']))
        
class settingTab(QFrame):
    def __init__(self, master, pos):
        super(settingTab, self).__init__(master)
        self.move(pos[0],pos[1])
        self.resize(winx-220,600)
        self.setStyleSheet('background-color: blue;')
        self.create()
    
    def gainchg(self):
        self.vgain.setText('%5d'%self.gain.value())
        self.appbtn.setStyleSheet(css['warnbutton'])

    def stimechg(self):
        self.vstime.setText('%5ds'%(self.stime.value()))
        self.appbtn.setStyleSheet(css['warnbutton'])
    
    def dtchg(self):
        self.vdt.setText('%5d'%(self.dt.value()))
        self.appbtn.setStyleSheet(css['warnbutton'])

    def avgchg(self):
        self.vavg.setText('%5d'%(self.avg.value()))
        self.appbtn.setStyleSheet(css['warnbutton'])
        
    def applySettings(self):
        adc_settings['gain'] = self.gain.value()
        adc_settings['tsample'] = self.stime.value()
        adc_settings['dt'] = self.dt.value()
        adc_settings['oversample'] = self.avg.value()
        
        with open(configfile, 'w') as f:
            json.dump(adc_settings, f)
            
        self.appbtn.setStyleSheet(css['button'])
        
    def create(self):
        label(self, 'DEVICE CONFIGURATION', (250,20))
        self.appbtn=cmdButton(self,'APPLY', (600, 500), (110,60), self.applySettings)
        
        label(self, 'GAIN',(20, 110))
        self.vgain=label(self,' 6',(700,110,100,30))
        self.gain=scroller(self, [200, 100, 500, 50], (0,6,1), self.gainchg)
        self.gain.setValue(adc_settings['gain'])
        
        label(self, 'SAMPLE TIME',(20, 190))
        self.vstime=label(self,'   60s',(700,190,100,30))
        self.stime=scroller(self, [200, 180, 500, 50], (10,3600,10), self.stimechg)
        self.stime.setValue(adc_settings['tsample'])
        
        label(self, 'SAMPLE PERIOD',(20, 270))
        self.vdt=label(self,'    0',(700,270,100,30))
        self.dt=scroller(self, [200, 260, 500, 50], (0,50,1), self.dtchg)
        self.dt.setValue(adc_settings['dt'])
        
        label(self, 'OVER SAMPLE', (20, 350))
        self.vavg=label(self, '    1',(700,350,100,30))
        self.avg=scroller(self, [200, 340, 500, 50], (1,20,1), self.avgchg) 
        self.avg.setValue(adc_settings['oversample'])
        
        self.appbtn.setStyleSheet(css['button'])
        
class helpTab(QFrame):
    def __init__(self, master, pos):
        super(helpTab, self).__init__(master)
        self.move(pos[0],pos[1])
        self.resize(winx-220,600)
        self.setStyleSheet('background-color: gray;')
        self.create()
    
    def create(self):
        web=QWebView(self)
        web.load(QUrl(docfile))


class SeismoWin(QMainWindow):
    
    def __init__(self):
        
        super(SeismoWin,self).__init__()
                
        self.setStyleSheet(css['main'])
        self.setGeometry(0,0,winx,winy)
        self.setWindowTitle("SEISMO-LOG")
        # self.setWindowIcon(QtGui.QIcon("pngfile");
        self.logtrd=None
        self.createWin()
        
    def clearAttr(self):
        self.cbut.setStyleSheet(css['button'])
        self.dbut.setStyleSheet(css['button'])
        self.sbut.setStyleSheet(css['button'])
        self.hbut.setStyleSheet(css['button'])
        self.ctab.hide()
        self.dtab.hide()
        self.stab.hide()
        self.htab.hide()
    
    def tabCtr(self):
        self.clearAttr()
        self.ctab.show()
        self.cbut.setStyleSheet(css['tabsel'])

    def tabData(self):
        self.clearAttr()
        self.dtab.show()
        self.dbut.setStyleSheet(css['tabsel'])
        self.dtab.datalist.update()
        self.dtab.ticks.start(5000)
        
    def tabSet(self):
        self.clearAttr()
        self.stab.show()
        self.sbut.setStyleSheet(css['tabsel'])
        
    def tabHelp(self):
        self.clearAttr()
        self.htab.show()
        self.hbut.setStyleSheet(css['tabsel'])
            
    def createWin(self):
        
        self.tframe=QFrame(self)
        self.tframe.resize(220,600)
        self.cbut=tabButton(self.tframe,'CONTROL',[10,50],act=self.tabCtr)
        self.dbut=tabButton(self.tframe,'DATAFILE', [10,150],act=self.tabData)
        self.sbut=tabButton(self.tframe,'SETTINGS',[10,250],act=self.tabSet)
        self.hbut=tabButton(self.tframe,'HELP',[10,350],act=self.tabHelp)
        
        self.ctab=controlTab(self, [220,0])
        self.dtab=dataTab(self, [220,0])
        self.stab=settingTab(self, [220,0])
        self.htab=helpTab(self, [220,0])
        
        self.tabCtr()
        
        if winmode == 'max':
            self.showMaximized()
        
        self.show()
    
    def startLogThread(self):
        # maybe reuseable??
        self.logtrd=Thread(target=adc.start,args=(adc_settings,))
        self.logtrd.start() 
    
    def stopLogThread(self):
        adc.stop()
    
    def closeEvent(self,ev):
        print('close application')
        
        if self.logtrd == None:
            return
            
        adc.logON.clear()
        adc.daemonRun.clear()
        
        while adc.logBusy.isSet():
            time.sleep(1)
        
        adc.logON.set()  # release event wait()
        
        if self.logtrd.is_alive():
            self.logtrd.join()       
 
####### MAIN ########
seismoapp=QApplication(sys.argv)
seismoGUI=SeismoWin()
seismoapp.exec()

if not stayon:
    print('Power down')
    os.system('sudo poweroff')
else:
    print('Seismo machine stays alive')
