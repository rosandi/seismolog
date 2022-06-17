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
from PyQt5.QtCore import Qt, QTimer, QUrl, QDate, QTime
from style import style as css
from plotter import plotter
import json
from datetime import datetime
from threading import Thread,Event
from queue import Queue
from PyQt5.QtWebKitWidgets import QWebView
from subprocess import check_output

def cmd(s):
    return check_output(s).decode('ascii')
    
winmode='max'
winx=1024
winy=600
configfile='/home/seismo/config.json'
errorfile='/home/seismo/seismo.err'
docfile='file:///home/seismo/doc/about-id.html'
dummy=False
dpath=None
stayon=False
netdev='wlan0'
restart_on_error=True
restartcnt=0

welcometxt='''
    <H1 style="text-align: center;">
    <br>SEISMO-LOG, 2021</H1>
    <div style="text-align: center;font-size:30px;">
    Geofisika<br>
    Universitas Padjadjaran
    </div>
    <br>
    <div style="text-align: center;font-size:16px;">
    Software version: seismoqt-1.0<br>
    ADC device: 24 bit, differential<br>
    <br>
'''

goodbyetxt='''
    <H2 style="text-align: center;"><br>System shutdown in 5 seconds</H2>
    <br>
    <div style="text-align: center;font-size:30px;">
    wait until shutdown complete <br>and turned off the power button!
    </div>
'''

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
    if arg.find('restart=') == 0:
        if arg.replace('restart=','') == 'yes':
            restart_on_error=True
        else:
            restart_on_error=False

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
        'format': 'column',
        'lon': 6.9175,
        'lat': 107.6191
    }

welcometxt+='date/time: '+QDate.currentDate().toString()
welcometxt+='/'+QTime.currentTime().toString()
welcometxt+='<br>coord: %0.5f, %05f'%(adc_settings['lon'], adc_settings['lat'])
welcometxt+='</div><br><br>'

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
        self.setStyleSheet(css['cmdbutton'])
        if (act != None):
            self.clicked.connect(act)

class statusText(QTextEdit):
    def __init__(self, master, pos, sz):
        super(statusText, self).__init__(master)
        self.move(pos[0],pos[1])
        self.resize(sz[0],sz[1])
        self.setStyleSheet(css['text'])
        self.setReadOnly(True)
        
class scroller(QSlider):
    def __init__(self, master, geo, lim=(0,100,1), proc=None):
        super(scroller,self).__init__(Qt.Horizontal,master)
        self.resize(geo[2],geo[3])
        self.move(geo[0],geo[1])
        self.setStyleSheet(css['scroll'])
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
        self.verticalScrollBar().setStyleSheet(css['scroll'])
        #self.setFlag(16)
            
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
            it=QListWidgetItem()
            it.setText(d.replace('.json',''))
            # it.setCheckState(Qt.Unchecked);
            self.addItem(it)
        
        
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
        
        if adc.daemonRun.isSet():
            s+='logging daemon active\n'
            if adc.logON.isSet():
                s+='acquisition on process, '
                sid=adc.statid
                s+='stage: '+adc.messages[sid]+'\n'
                if sid != 0:
                    tlog=adc.tend-adc.tstart
                    tnow=time.time()-adc.tstart
                    s+='#log %d time: %0.2f sec from %0.2f sec\n'%(adc.lognum,tnow,tlog)
            else:
                s+='idle\n'
        else:
            s+='logging daemon stopped\n'
        
        self.devstat.setText(s)
        mx=self.devstat.verticalScrollBar().maximum()
        self.devstat.verticalScrollBar().setValue(mx)
        
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

        mx=self.devstat.verticalScrollBar().maximum()
        self.devstat.verticalScrollBar().setValue(mx)
 
    def device_shutdown(self):
        self.devstat.setText(goodbyetxt)
        QTimer().singleShot(5000, lambda: seismoGUI.close())
            
    def create(self):
        self.devstat=statusText(self, [10,100], [760,400])
        self.statusBtn=cmdButton(self,'STATUS', (20,10), (150,60), self.status)
        self.startBtn=cmdButton(self,'START', (200,10), (150,60), self.startLog)
        self.clearBtn=cmdButton(self,'CLEAR', (20,510), (150,60), lambda: self.devstat.setText(''))
        self.pdownBtn=cmdButton(self,'QUIT', (520,510), (220,60), self.device_shutdown)
        
        self.clearBtn.setStyleSheet(css['button']);
        self.pdownBtn.setStyleSheet(css['warnbutton']);
        
        self.devstat.setHtml(welcometxt)

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
        
        self.plotx=plotter(self, [10, 10, 540, 180], 'X-comp')        
        self.ploty=plotter(self, [10, 200, 540, 180], 'Y-comp')        
        self.plotz=plotter(self, [10, 390, 540, 180], 'Z-comp')
        
        self.datalist=dataList(self, [560, 30, 245,400], adc_settings['datapath'])
        self.dinfo=statusText(self, [560,440], [235,130])
        self.ticks=QTimer()
        self.ticks.timeout.connect(lambda: self.update_to())

    def hide(self):
        self.plotx.data=None
        self.ploty.data=None
        self.plotz.data=None
        super(dataTab, self).hide()
        
    def plot(self, dname):
        
        # this gives confusion...
        #if adc.logBusy.isSet():
        #    return
                
        try:
            with open(dname) as f:
                d=json.load(f)
            
            self.plotx.lim=(0,d['tsample'])
            self.ploty.lim=(0,d['tsample'])
            self.plotz.lim=(0,d['tsample'])
            
            self.plotx.plot(d['data'][0])
            self.ploty.plot(d['data'][1])
            self.plotz.plot(d['data'][2])
            logtime=datetime.fromtimestamp(d['tstart']).strftime("%m/%d/%Y %H:%M:%S")
            dinfo=self.dinfo
            nn=dname.split('/')
            nn=nn[len(nn)-1].replace('.json','')
            dinfo.setText(nn+'\n\n'+logtime+'\ntsample:%0.5e\nlength:%d'%(d['tsample'],d['length']))
        except:
            print('bad data format')

class networkDialog(QDialog):
    def __init__(self,master):
        super(networkDialog,self).__init__(master)
        self.setModal(True)
        self.move(450,250)
        self.resize(300,200)
        self.iplabel=label(self, 'Waiting for address',(20,20,300,20))
        self.closebtn=cmdButton(self, 'CLOSE', (80, 120), (140,60), lambda: self.close())
        self.closebtn.setEnabled(False)
        self.closebtn.setStyleSheet(css['button'])
        self.wcount=0
        self.ipwait=QTimer()
        self.ipwait.timeout.connect(lambda: self.waitwlan())

        ip=self.checkwlan()
        if ip == None:
            os.system('sudo service dhcpcd start &')
        self.waitwlan()    

    def checkwlan(self):
        ip=None
        try:
            st=cmd(['ip','add','show',netdev])
            for s in st.split('\n'):
                ln=s.strip()
                if ln.find('inet ') == 0:
                    ip=ln.split()[1]
                    break
        except:
            pass
            
        return ip
        
    def waitwlan(self):
        ip=self.checkwlan()
        if ip == None and self.wcount < 50:
            self.wcount+=1
            self.ipwait.start(1000)
            #print("waiting... ip=",ip)

        elif self.wcount >=50:
            self.iplabel.setText('failed to activate WiFi')
            self.closebtn.setEnabled(True)            
        else:
            self.iplabel.setText('IP Address: '+ip)
            self.closebtn.setEnabled(True)


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
        self.vdt.setText('%5ds'%(self.dt.value()))
        self.appbtn.setStyleSheet(css['warnbutton'])

    def avgchg(self):
        self.vavg.setText('%5d'%(self.avg.value()))
        self.appbtn.setStyleSheet(css['warnbutton'])
    
    def everychg(self):
        self.vevery.setText('%5ds'%(self.every.value()))
        self.appbtn.setStyleSheet(css['warnbutton'])
        
    def applySettings(self):
        adc_settings['gain'] = self.gain.value()
        adc_settings['tsample'] = self.stime.value()
        adc_settings['dt'] = self.dt.value()
        adc_settings['oversample'] = self.avg.value()
        adc_settings['every'] = self.every.value()
        
        with open(configfile, 'w') as f:
            json.dump(adc_settings, f)
            
        self.appbtn.setStyleSheet(css['button'])
        
    def resetSettings(self):
        self.gain.setValue(adc_settings['gain'])
        self.stime.setValue(adc_settings['tsample'])
        self.dt.setValue(adc_settings['dt'])
        self.avg.setValue(adc_settings['oversample'])
        self.every.setValue(adc_settings['every'])
        self.appbtn.setStyleSheet(css['button'])
        
    def create(self):
        label(self, 'DEVICE CONFIGURATION', (250,20))
        self.appbtn=cmdButton(self,'APPLY', (600, 500), (120,60), self.applySettings)
        self.cancelbtn=cmdButton(self,'RESET', (430, 500), (140,60), self.resetSettings)
        
        sy=80
        label(self, 'GAIN',(20, sy+10))
        self.vgain=label(self,'%5d'%(adc_settings['gain']),(700,sy+10,100,30))
        self.gain=scroller(self, [200, sy, 500, 50], (0,6,1), self.gainchg)
        self.gain.setValue(adc_settings['gain'])
    
        sy+=80
        label(self, 'SAMPLE TIME',(20, sy+10))
        self.vstime=label(self,'%5ds'%(adc_settings['tsample']),(700,sy+10,100,30))
        self.stime=scroller(self, [200, sy, 500, 50], (10,3600,10), self.stimechg)
        self.stime.setValue(adc_settings['tsample'])
        
        sy+=80
        label(self, 'SAMPLE PERIOD',(20, sy+10))
        self.vdt=label(self,'%5ds'%(adc_settings['dt']),(700,sy+10,100,30))
        self.dt=scroller(self, [200, sy, 500, 50], (0,50,1), self.dtchg)
        self.dt.setValue(adc_settings['dt'])
        
        sy+=80
        label(self, 'OVER SAMPLE', (20, sy+10))
        self.vavg=label(self, '%5d'%(adc_settings['oversample']),(700,sy+10,100,30))
        self.avg=scroller(self, [200, sy, 500, 50], (1,20,1), self.avgchg) 
        self.avg.setValue(adc_settings['oversample'])
        
        sy+=80
        label(self, 'ACQ PERIOD', (20, sy+10))
        self.vevery=label(self, '%5ds'%(adc_settings['every']),(700,sy+10,100,30))
        self.every=scroller(self, [200, sy, 500, 50], (0,3600,10), self.everychg) 
        self.every.setValue(adc_settings['every'])
        
        self.appbtn.setStyleSheet(css['button'])
        self.cancelbtn.setStyleSheet(css['button'])       

class systemTab(QFrame):
      
    def __init__(self, master, pos):
        super(systemTab, self).__init__(master)
        self.move(pos[0],pos[1])
        self.resize(winx-220,600)
        self.setStyleSheet('background-color: blue;')
        self.create()
    
    def enableWifi(self):
        if dummy:
            return
        networkDialog(seismoGUI).exec()
        
    def dataman(self):
        print('data manager') # FIXME! module
        os.system('/home/seismo/bin/fileman &')
 
    def apply(self):
        d=self.datein.date()
        th=self.hourin.value()
        tm=self.minin.value()
        ts=self.secin.value()
        sd='%04d-%02d-%02d %02d:%02d:%02d'%(d.year(),d.month(),d.day(),th,tm,ts)
        sd=cmd(['date','--date='+sd])
        print('set date: ',d)
        os.system('sudo date --set="'+sd+'"')
        
        adc_settings['lat']=self.lat.value()
        adc_settings['lon']=self.lon.value()

        with open(configfile, 'w') as f:
            json.dump(adc_settings, f)
        
        print(cmd('date'))
    
    def create(self):
        self.datein=QDateEdit(QDate.currentDate(),self,calendarPopup=True)
        
        sy=80
        label(self,'DATE/TIME',(20,sy+10))
        self.datein.move(180,sy)
        self.datein.setStyleSheet(css['dtime'])
        
        tm=QTime.currentTime()
        label(self,'H',(430,sy+10))
        self.hourin=QSpinBox(self)
        self.hourin.move(450,sy)
        self.hourin.setMinimum(0)
        self.hourin.setMaximum(23)
        self.hourin.setStyleSheet(css['dtime'])
        self.hourin.setValue(tm.hour())

        label(self,'M',(550,sy+10))        
        self.minin=QSpinBox(self)
        self.minin.move(570,sy)
        self.minin.setMinimum(0)
        self.minin.setMaximum(60)
        self.minin.setStyleSheet(css['dtime'])
        self.minin.setValue(tm.minute())
        
        label(self,'S',(670,sy+10))
        self.secin=QSpinBox(self)
        self.secin.move(690,sy)
        self.secin.setMinimum(0)
        self.secin.setMaximum(60)
        self.secin.setStyleSheet(css['dtime'])
        self.secin.setValue(tm.second())
        
        sy+=80
        label(self,'LONGITUDE',(20,sy+10))
        self.lon=QDoubleSpinBox(self)
        self.lon.move(180,sy)
        self.lon.setMinimum(-180)
        self.lon.setMaximum(180)
        self.lon.setDecimals(5)
        self.lon.setValue(adc_settings['lon'])
        self.lon.setStyleSheet(css['dtime'])
        
        label(self,'LATITUDE',(435,sy+10))
        self.lat=QDoubleSpinBox(self)
        self.lat.move(555,sy)
        self.lat.setMinimum(-180)
        self.lat.setMaximum(180)
        self.lat.setDecimals(5)
        self.lat.setValue(adc_settings['lat'])
        self.lat.setStyleSheet(css['dtime'])

        sy+=80
        self.wifibtn=cmdButton(self,'WiFi', (180,sy), (280,60), self.enableWifi)
        
        sy+=80
        cmdButton(self,'DATA MANAGER', (180,sy), (280,60), self.dataman)
        
        
        self.appbtn=cmdButton(self,'APPLY', (600,500), (120,60), self.apply)
        self.appbtn.setStyleSheet(css['button'])
        
    def update_time(self):
        d=QDate.currentDate()
        t=QTime.currentTime()
        self.datein.setDate(d)
        self.hourin.setValue(t.hour())
        self.minin.setValue(t.minute())
        self.secin.setValue(t.second())

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
        self.sybut.setStyleSheet(css['button'])
        self.hbut.setStyleSheet(css['button'])
        self.ctab.hide()
        self.dtab.hide()
        self.stab.hide()
        self.sytab.hide()
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
    
    def tabSystem(self):
        self.clearAttr()
        self.sytab.update_time()
        self.sytab.show()
        self.sybut.setStyleSheet(css['tabsel'])

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
        self.sybut=tabButton(self.tframe,'SYSTEM',[10,350],act=self.tabSystem)
        self.hbut=tabButton(self.tframe,'HELP',[10,450],act=self.tabHelp)
        
        self.ctab=controlTab(self, [220,0])
        self.dtab=dataTab(self, [220,0])
        self.stab=settingTab(self, [220,0])
        self.sytab=systemTab(self, [220,0])
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

def main():
    global seismoGUI, stayon
    
    seismoapp=QApplication(sys.argv)
    seismoGUI=SeismoWin()
    seismoapp.exec()

#    if not stayon:
#        print('Power down')
#        os.system('sudo poweroff')
#    else:
#        print('Seismo machine stays alive')


try:
    main()

except Exception as e:
    print('SEISMOLOG PROGRAM ERROR:')
    print(e)
    
    with open(errorfile,'a') as f:
        f.write(string(e));
        f.write('\nerror count %d\n'%(restartcnt))
    
    if restart_on_error:
        restartcnt+=1
        print('restarting application')
        main()
