#!/usr/bin/python3

import json
import sys
import os
from datetime import date,datetime

datapath=sys.argv[1]

try:
    when=datetime.strptime(sys.argv[2],"%d-%m-%Y %H:%M:%S")
    when=datetime.timestamp(when)
except Exception as e:
    print(e)
    print('using today')
    when=date.today()
    when=datetime.timestamp(datetime.combine(when,datetime.min.time()))

VC=[]

for df in os.listdir(datapath):
    if df.find('.json',len(df)-5) > 0:
        with open(datapath+'/'+df) as fl:
            v=json.load(fl)
        dt=v['tstart']-when
        if dt > 0:
            VC.append((dt, v['voltage'], v['current']))

VC=sorted(VC,key=lambda v: v[0])

for v in VC:
    print(v[0], v[1], v[2])
