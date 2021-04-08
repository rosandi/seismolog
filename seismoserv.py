#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler,HTTPServer
import sys
import os
import json

from subprocess import check_output as cmd
from time import sleep,time

sleeplength=0.01
host=''
port=8000
app='yrapp.html'
datapath='.'
progpath='./'
mainprog='seismolog'

for arg in sys.argv:
    if arg.find('host=') == 0:
        host=arg.replace('host=','')
    if arg.find('port=') == 0:
        port=arg.replace('port=','')

busy=False

def checkstatus():
        st=False
        cout=cmd(['ps', '-e']).decode('ascii').split('\n')
        
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
    
    
    def do_GET(self):
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
            print('sent app.html')
            
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
                
        elif htfile == 'status':
            s=json.dumps({'status':checkstatus()})
            self.header('text/json')
            self.wfile.write(bytes(s,'utf-8'))
        
        elif htfile == 'start':
            prg=progpath+mainprog
            if not checkstatus():
                ret=os.system('nohup {} 2>/dev/null &'.format(prg))
                print('running logging daemon {}: {}'.format(prg,ret))
                
            s=json.dumps({'status':checkstatus()})
            self.header('text/json')
            self.wfile.write(bytes(s,'utf-8'))
        
        elif htfile == 'stop':
            if checkstatus():
                os.system('killall '+mainprog)
                print('killing logging daemon')
                
            s=json.dumps({'status':checkstatus()})
            self.header('text/json')
            self.wfile.write(bytes(s,'utf-8'))
                 
        elif htfile == 'list':
            datafiles=[]
            for df in os.listdir(datapath):
                if df.rfind('.json') > 0:
                    datafiles.append(df)
            
            datafiles=json.dumps({'files':datafiles})
            self.header('text/json')
            self.wfile.write(bytes(datafiles),'utf-8')
        
        elif htfile == 'shutdown':
            self.header('text/plain')
            self.wfile.write(bytes('system shutdown','utf-8'))
            os.system('sudo poweroff &')

################ MAIN PROGRAM ###############

print("serving on %s:%s"%(host,port))

try:
    with HTTPServer((host,int(port)), OtherApiHandler) as server:
        server.serve_forever()
        
except KeyboardInterrupt:
    print("\nterminating server")
    print("bye...")
