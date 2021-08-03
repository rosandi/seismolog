#!/usr/bin/env python3

import time
from SX127x.LoRa import *
from SX127x.board_config import BOARD

BOARD.setup()
BOARD.reset()

MSGHEAD=[255, 255, 0, 0]
MSGTAIL=[0]
CHUNKSIZE=16-len(MSGTAIL)-len(MSGTAIL)

def msgfmt(msg,eof=True):
    msg=MSGHEAD+[ord(m) for m in msg]
    if eof:
        msg+=MSGTAIL
    return msg

def msgstr(msg):
    msg=bytes(msg).decode("utf-8",'ignore')
    body=msg[len(MSGHEAD)-2:-len(MSGTAIL)]
    tail=msg[-len(MSGTAIL):]
    return body,tail

class Sender(LoRa):
    sent=False
    cnt=0
    nlines=0
    content=''
    
    def __init__(self, fname, verbose=False):
        super(Sender, self).__init__(verbose)
        self.fname=fname
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True )# Receive INF
        mens,_=msgstr(payload)
        if mens=="INF":
            if self.cnt <= self.nlines: # one extra line: filename
                print("Received data request INF")
                time.sleep(2)
                self.write_payload(msgfmt(self.content[self.cnt]))
                self.set_mode(MODE.TX)
                print("sending: "+self.content[self.cnt])
                self.cnt+=1
                time.sleep(2)
            else:
                print("end of file...")
                self.sent=True
        elif mens == 'ACK':
            print('acknowledged sent')
            self.sent=True

        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)
        time.sleep(2)

    def start(self):
                  
        with open(self.fname) as fd:
            st=fd.read()
            st=[st[s:s+CHUNKSIZE] for s in range(0,len(st), CHUNKSIZE)]
            st[len(st)-1]+='\0'

        self.content=[self.fname]+st
        self.nlines=len(st)
        while not self.sent:
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT)
            time.sleep(2)
            while not self.sent:
                pass

lora = Sender('tosend.txt',verbose=False)
lora.set_pa_config(pa_select=1, max_power=21, output_power=15)
lora.set_bw(BW.BW125)
lora.set_coding_rate(CODING_RATE.CR4_8)
lora.set_spreading_factor(12)
lora.set_rx_crc(True)
lora.set_low_data_rate_optim(True)

assert(lora.get_agc_auto_on() == 1)

try:
    print("START")
    lora.start()
except KeyboardInterrupt:
    sys.stdout.flush()
    print("Exit")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("Exit")
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()
