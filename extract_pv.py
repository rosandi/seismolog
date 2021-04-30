#!/usr/bin/python3

import json
import sys
import os
import math
from datetime import date,datetime

# $1 = directory, $2 = start date-time, $3 = end date

datapath=sys.argv[1]

try:
    mintime=datetime.strptime(sys.argv[2],"%d-%m-%Y %H:%M:%S")
    mintime=datetime.timestamp(mintime)
except Exception as e:
    print(e)
    print('using from today', file=sys.stderr)
    mintime=date.today()
    mintime=datetime.timestamp(datetime.combine(mintime,datetime.min.time()))

try:
    maxtime=datetime.strptime(sys.argv[3],"%d-%m-%Y %H:%M:%S")
    maxtime=datetime.timestamp(maxtime)
except Exception as e:
    print(e)
    print('using to today', file=sys.stderr)
    maxtime=date.today()
    maxtime=datetime.timestamp(datetime.combine(maxtime,datetime.max.time()))

VC=[]

for df in os.listdir(datapath):
    if df.find('.json',len(df)-5) > 0:
        with open(datapath+'/'+df) as fl:
            v=json.load(fl)
        dt=v['tstart']-mintime
        du=v['tstart']-maxtime
        if dt > 0 and du < 0:
            VC.append((dt, v['voltage'], v['current']))

VC=sorted(VC,key=lambda v: v[0])

for v in VC:
    print(v[0], v[1], v[2])
