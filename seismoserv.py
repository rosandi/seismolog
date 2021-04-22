#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler,HTTPServer
import sys
import os
import json
import markdown as md

from subprocess import check_output
from time import sleep,time

version='1.0 (c) 2021, rosandi'
sleeplength=0.01
host=''
port=8000
app='yrapp.html'
datapath='/home/pi/data'
progpath='./'
settings='chanmask=7:block=2048:avg=1:delay=0:lat=0:lon=0:dir='+datapath
mainprog='seismolog'

for arg in sys.argv:
    if arg.find('host=') == 0:
        host=arg.replace('host=','')
    if arg.find('port=') == 0:
        port=arg.replace('port=','')
    if arg.find('dir=') == 0:
        datapath=arg.replace('dir=','')


ret=os.system('mkdir -p {}'.format(datapath))

if ret != 0:
    exit(0)

busy=False

def cmd(s):
    return check_output(s).decode('ascii')

def checkstatus():
        st=False
        cout=cmd(['ps', '-e']).split('\n')
        
        for c in cout:
            if c.find('seismolog') > 0:
                st=True
                break

        return st
            
class OtherApiHandler(BaseHTTPRequestHandler):
   
    def header(self,mime):
        self.send_response(200)
        self.send_header('Content-type',mime)
        self.end_headers()
        
    def response(self,text,mime='text/plain'):
        self.send_response(200)
        self.send_header('Content-type',mime)
        self.end_headers()
        self.wfile.write(bytes(text,'utf-8'))        
    
    def do_GET(self):
        global settings,datapath
        
        acmd=self.requestline.split()
        print('Get request received',acmd)
        
        if len(acmd) < 1:
            self.send_response(400,"invalid response")

        htfile=acmd[1].replace('/',' ').strip()

        if htfile == '' or htfile=='app':
            self.header('text/html')
            appfile=open(app,mode='r')
            htcontent=appfile.read()
            appfile.close()
            self.wfile.write(bytes(htcontent,'utf-8'))
            print('sent: ', app)
            
        elif htfile == 'favicon.ico':
            self.header('image/x-icon')
            icofile=open('favicon.ico',mode='rb')
            ico=icofile.read()
            icofile.close()
            self.wfile.write(ico)
            
        elif htfile.rfind('.js',len(htfile)-3)>0:
            # we may limit only to specific javascripts
            self.header('text/plain')
            try:
                jsfile=open(htfile,mode='r')
                htcontent=jsfile.read()
                jsfile.close()
                self.wfile.write(bytes(htcontent,'utf-8'))
                print('sent script: {}'.format(htfile))
            except:
                self.wfile.write(bytes("/* file not found {} */".format(htfile),'ascii'))
        
        elif htfile.rfind('.png',len(htfile)-4)>0:
            print('image:',htfile)
            self.header('image/png')
            imgfl=open(progpath+'/doc/'+htfile,'rb')
            img=imgfl.read()
            imgfl.close()
            self.wfile.write(img)
        
        elif htfile == 'status':
            uptime=cmd('uptime')
            disk=cmd(['df', '-h', '--output=size,used,avail,pcent', '/']).split('\n')
            s={'status':checkstatus(),'uptime':uptime,'disk':disk}
            s=json.dumps(s)
            self.header('text/json')
            self.wfile.write(bytes(s,'utf-8'))
        
        elif htfile == 'start':
            prg=progpath+mainprog+' '+settings.replace(':',' ')
            if not checkstatus():
                ret=os.system('nohup {} 2>/dev/null &'.format(prg))
                print('running logging daemon ',prg)
                
            s=json.dumps({'status':checkstatus(),'program':prg})
            self.header('text/json')
            self.wfile.write(bytes(s,'utf-8'))
        
        elif htfile == 'stop':
            if checkstatus():
                os.system('killall '+mainprog)
                print('killing logging daemon')
                
            s=json.dumps({'status':checkstatus()})
            self.header('text/json')
            self.wfile.write(bytes(s,'utf-8'))
                 
        elif htfile.find('list') == 0:
            datafiles=[]
            sr=htfile.split()
            ext='.'+sr[1]
            
            checkcnt=False
            if len(sr) == 3:
                if sr[2] == 'count':
                    checkcnt=True

            print('list ext: *'+ext)

            for df in os.listdir(datapath):
                if df.rfind(ext) > 0:
                    datafiles.append(df)
                    
            cnt=len(datafiles)
            if checkcnt:
                self.response(json.dumps({'count':cnt}))
            else:
                datafiles.sort(reverse=True)
                self.response(json.dumps({'count':cnt,'files':datafiles}))
        
        elif htfile.find('load')==0:
            fname=datapath+'/'+htfile.replace('load ','')
            try:
                fl=open(fname)
                data=json.load(fl)
                fl.close()
                self.header('text/json')
                self.wfile.write(bytes(json.dumps(data),'utf-8'))           
            except:
                self.header('text/json')
                self.wfile.write(bytes('--','utf-8'))   
            
        elif htfile == 'shutdown':
            self.header('text/plain')
            self.wfile.write(bytes('system shutdown','utf-8'))
            sleep(5)
            os.system('sudo poweroff &')
            
        elif htfile.find('par ') == 0:
            settings=htfile.replace('par ','')
            print('parameter request: '+settings)
            s='Logging parameters:<br>'+settings
            if settings.find('dir=') < 0:
                settings+=':dir='+datapath
            self.header('text/plain')
            self.wfile.write(bytes(s,'utf-8'))
        
        elif htfile.find('set ') == 0:
            sreq=htfile.replace('set ','').split()
            for s in sreq:
                if s.find('date=') == 0: ## let use this format YY-mm-dd+HH:MM:SS
                    d=s.replace('date=','').replace('+',' ')
                    d=cmd(['date','--date='+d])
                    print('set date: ',d)
                    os.system('sudo date --set="'+d+'"')
                    self.response(cmd('date'))
                elif s.find('dir=') == 0:
                    datapath=s.replace('dir=','')
                    self.response('data directory set to '+datapath)
                else:
                    self.response('invalid set command: '+s)
        
        elif htfile.find('get ') == 0:
            sreq=htfile.replace('get ','').split()
            for s in sreq:
                print(s)
                if s.find('free') == 0:
                    ss=cmd(['df','/','--output=pcent'])
                    ss=str(100-int(ss.replace('\n',' ').replace('%','').split[1]))
                    self.response(ss)
                
                elif s.find('settings') == 0:
                    rs=settings.split(':')
                    js=''
                    for ss in rs:
                        ss=ss.split('=')
                        js+=' "'+ss[0]+'":'+ss[1]
                    
                    rs='{'+js.strip().replace(' ',',').replace('"dir":','"dir":"')+'"}'
                    self.response(rs)
                
                elif s.find('about') == 0:
                    afl=open(progpath+'/doc/about-id.md','r')
                    about=md.markdown(afl.read())
                    afl.close()
                    self.response(about)
                    
                elif s.find('version') == 0:
                    self.response(version)
        
        else:
            print('unimplemented request: ',htfile)
            self.header('text/plain')
            self.wfile.write(bytes('unimplemented request: '+htfile,'utf-8'))
            

################ MAIN PROGRAM ###############

print("serving on %s:%s"%(host,port))

try:
    with HTTPServer((host,int(port)), OtherApiHandler) as server:
        server.serve_forever()
        
except KeyboardInterrupt:
    print("\nterminating server")
    print("bye...")
