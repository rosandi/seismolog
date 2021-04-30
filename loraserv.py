#!/usr/bin/env python3

import time
from SX127x.LoRa import *
from SX127x.board_config import BOARD

BOARD.setup()
BOARD.reset()

MSGHEAD=[255, 255, 0, 0]
MSGTAIL=[0]

def msgfmt(msg):
    msg=[ord(m) for m in msg]
    return MSGHEAD+msg+MSGTAIL

def msgstr(msg):
    msg=bytes(msg).decode("utf-8",'ignore')
    body=msg[len(MSGHEAD)-2:-len(MSGTAIL)]
    tail=msg[-len(MSGTAIL):]
    return body,tail

class Receiver(LoRa):
    recvbuf=''
    fname='tmp.txt'
    cnt=0
    
    def __init__(self, verbose=False):
        super(Receiver, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0] * 6)
        self.var=0

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        msg,_=msgstr(payload)

        if self.cnt == 0:
            self.fname == msg
        else:
            self.recvbuf+=msg

        print ("Received: "+msg)
        
        if msg[-1:] == '\0':
            time.sleep(2)
            print ("Send: ACK")
            self.write_payload(msgfmt('ACK'))
            self.set_mode(MODE.TX)
            with open(self.fname,'w') as fd:
                fd.write(self.recvbuf[:-1])
        
        self.cnt+=1
        self.var=1

    def start(self):          
        while True:
            while (self.var==0):
                print ("Send: INF")
                self.write_payload(msgfmt('INF'))
                self.set_mode(MODE.TX)
                time.sleep(2)
                self.reset_ptr_rx()
                self.set_mode(MODE.RXCONT) # Receiver mode
            
                start_time = time.time()
                while (time.time() - start_time < 10): # wait until receive data or 10s
                    pass;
            
            self.var=0
            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT) # Receiver mode
            time.sleep(10)

lora = Receiver(verbose=False)
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
