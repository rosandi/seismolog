from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QDialog, QScrollBar, QLabel, QPushButton, QCheckBox
from PyQt5.QtGui import QPainter, QColor, QFont, QPainterPath, QPen
import numpy as np
from scipy.fftpack import fft
from style import style as css

class plotScroller:
    def update_val(self, proc):
        d=str(self.scl.value())
        self.v.setText(d)
        if proc != None:
            proc(self.scl.value())
        
    def __init__(self, master, text, geo, proc=None, lim=(0,100,1)):
        self.scl=QScrollBar(Qt.Horizontal, master)
        self.scl.resize(geo[2]-50,geo[3])
        self.scl.move(geo[0]+50,geo[1])
        self.scl.setMinimum(lim[0])
        self.scl.setMaximum(lim[1])
        self.scl.setSingleStep(lim[2])
        self.scl.valueChanged.connect(lambda: self.update_val(proc))
        
        q=QLabel(master)
        q.move(geo[0],geo[1]+10)
        q.resize(50,20)
        q.setText(text)
        
        self.v=QLabel(master)
        self.v.move(geo[2]+10,geo[1]+10)
        self.v.resize(50,20)
        self.v.setText(str(self.scl.value()))
    
    def setValue(self, v):
        self.scl.setValue(v)

class plotDialog(QDialog):
    def __init__(self, master, pos, title=''):
        super(plotDialog,self).__init__(master)
        self.title=title
        self.plotter=master
        self.setModal(True)
        self.resize(400,350)
        self.move(pos[0],pos[1])
        self.setStyleSheet(css['dialog'])
        self.setWindowOpacity(0.75)
        self.create()   
        self.exec()
        
    def change_scale(self,v):
        self.plotter.scale=v
        self.plotter.repaint()

    def change_zoom(self,v):
        self.plotter.zoom=v
        self.plotter.repaint()

    def change_xpan(self,v):
        self.plotter.xpan=v
        self.plotter.repaint()

    def change_ofs(self,v):
        self.plotter.yofs=v
        self.plotter.repaint()
        
    def change_fft(self,v):
        self.plotter.fft=v
        self.plotter.repaint()
        
    def create(self):
        nm=QLabel(self)
        nm.move(200,5)
        nm.setText(self.title)
        
        plotScroller(self, 'SCALE', (5,20,350,50), lambda v: self.change_scale(v)).setValue(self.plotter.scale)
        plotScroller(self, 'OFFSET', (5,85,350,50), lambda v:self.change_ofs(v), (-1000,1000,1)).setValue(self.plotter.yofs)
        plotScroller(self, 'ZOOM', (5,150,350,50), lambda v:self.change_zoom(v), (-100,0,1)).setValue(self.plotter.zoom)
        plotScroller(self, 'XPAN', (5,215,350,50), lambda v:self.change_xpan(v)).setValue(self.plotter.xpan)
        
        ck=QCheckBox('FFT', self)
        ck.setCheckState(self.plotter.fft)
        ck.move(20,280)
        ck.setStyleSheet(css['ctext'])
        ck.clicked.connect(lambda: self.change_fft(ck.checkState()))
        
        c=QPushButton('RESET', self)
        c.move(150,280)
        c.resize(120,60)
        c.setStyleSheet(css['button'])
        c.clicked.connect(lambda: self.plotter.resetplot())

        b=QPushButton('CLOSE', self)
        b.move(275,280)
        b.resize(120,60)
        b.setStyleSheet(css['button'])
        b.clicked.connect(lambda: self.close())
        
class plotter(QFrame):

    def __init__(self, master, geo, name=''):
        super(plotter,self).__init__(master)
        self.name=name
        self.dim=geo[2:]
        self.resize(geo[2],geo[3])
        self.move(geo[0],geo[1])
        self.setStyleSheet('background-color: white;')
        self.scale=40 # logaritmic FIXME: silent amplitude
        self.zoom=0 # logaritmic
        self.xpan=0
        self.yofs=0
        self.data=None
        self.invert=True
        self.fft=False
                
    def paintEvent(self, event):
        p=QPainter(self)
        
        self.axis(p)
        
        if self.data != None:
            if self.fft:
                self.plotvsfreq(p)
            else:
                self.plotvstime(p)
            
    def axis(self,p):
        x=self.dim        
        p.setPen(QColor(168, 34, 3))
        p.setFont(QFont('Decorative', 10))
        p.drawLine(20, 5, 20, x[1]-5)
        if not self.fft:
            p.drawLine(20, x[1]/2, x[0]-5, x[1]/2)
 
    def plotvstime(self,p):
        xmax=len(self.data)
        g=10**(self.scale/10)
        zo=int(np.round(xmax*2**(self.zoom/10)))
        ofs=int(xmax*self.xpan/100)
        dview=[]
        
        if zo>=xmax:
            zo=xmax

        if ofs>xmax-zo:
            ofs=xmax-zo
        
        for d in range(ofs, ofs+zo):
            if d > xmax:
                break
            dview.append(self.data[d]*g)
        
        x=20
        dx=((self.dim[0]-20)/len(dview))
        yzero=self.dim[1]/2+self.yofs/5 # FIXME!

        line=QPainterPath()
        line.moveTo(x,yzero)
        
        for d in dview:
            if self.invert:
                line.lineTo(x,yzero+d)
            else:
                line.lineTo(x,yzero-d)
            x+=dx
            
        p.setPen(QPen(Qt.red,  2, Qt.SolidLine))
        # p.setRenderHint(QPainter.Antialiasing)
        p.drawPath(line)
        
    def plotvsfreq(self,p):
        xmax=int(len(self.data)/2)
        g=10**(self.scale/10)
        zo=int(np.round(xmax*2**(self.zoom/10)))
        ofs=int(xmax*self.xpan/100)

        dview=np.abs(fft(self.data))
        dview[0]=0
        m=np.amax(dview) # normalization
        dview*=self.dim[1]/m
        
        dview=dview[ofs:(ofs+zo)]
        
        x=20
        dx=((self.dim[0]-20)/len(dview))
        yzero=self.dim[1] # FIXME!

        line=QPainterPath()
        line.moveTo(x,yzero)
        
        for d in dview:
            line.lineTo(x,yzero-d)
            x+=dx            

        p.setPen(QPen(Qt.red,  2, Qt.SolidLine))
        # p.setRenderHint(QPainter.Antialiasing)
        p.drawPath(line)
    
    def plot(self,data):
        
        self.data=data
        self.repaint()
        
    def resetplot(self):
        self.scale=40 # logaritmic FIXME: silent amplitude
        self.zoom=0 # logaritmic
        self.xpan=0
        self.yofs=0
        self.repaint()        

    def mousePressEvent(self,ev):
        plotDialog(self,(600,200),self.name)

