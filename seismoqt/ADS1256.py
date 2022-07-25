import RPi.GPIO as GPIO
import spidev
import time

spi=spidev.SpiDev(0, 0)
RST_PIN  = 18
CS_PIN   = 22
DRDY_PIN = 17

# data rate
DRATE_E = {'30000SPS' : 0xF0, # reset the default values
           '15000SPS' : 0xE0,
           '7500SPS' : 0xD0,
           '3750SPS' : 0xC0,
           '2000SPS' : 0xB0,
           '1000SPS' : 0xA1,
           '500SPS' : 0x92,
           '100SPS' : 0x82,
           '60SPS' : 0x72,
           '50SPS' : 0x63,
           '30SPS' : 0x53,
           '25SPS' : 0x43,
           '15SPS' : 0x33,
           '10SPS' : 0x20,
           '5SPS' : 0x13,
           '2d5SPS' : 0x03
          }

# registration definition
REG_E = {'STATUS': 0,  # x1H
         'MUX'   : 1,  # 01H
         'ADCON' : 2,  # 20H
         'DRATE' : 3,  # F0H
         'IO'    : 4,  # E0H
         'OFC0'  : 5,  # xxH
         'OFC1'  : 6,  # xxH
         'OFC2'  : 7,  # xxH
         'FSC0'  : 8,  # xxH
         'FSC1'  : 9,  # xxH
         'FSC2'  :10,  # xxH
        }

# command definition
CMD = {'WAKEUP' : 0x00,     # Completes SYNC and Exits Standby Mode 0000  0000 (00h)
       'RDATA' : 0x01,      # Read Data 0000  0001 (01h)
       'RDATAC' : 0x03,     # Read Data Continuously 0000   0011 (03h)
       'SDATAC' : 0x0F,     # Stop Read Data Continuously 0000   1111 (0Fh)
       'RREG' : 0x10,       # Read from REG rrr 0001 rrrr (1xh)
       'WREG' : 0x50,       # Write to REG rrr 0101 rrrr (5xh)
       'SELFCAL' : 0xF0,    # Offset and Gain Self-Calibration 1111    0000 (F0h)
       'SELFOCAL' : 0xF1,   # Offset Self-Calibration 1111    0001 (F1h)
       'SELFGCAL' : 0xF2,   # Gain Self-Calibration 1111    0010 (F2h)
       'SYSOCAL' : 0xF3,    # System Offset Calibration 1111   0011 (F3h)
       'SYSGCAL' : 0xF4,    # System Gain Calibration 1111    0100 (F4h)
       'SYNC' : 0xFC,       # Synchronize the A/D Conversion 1111   1100 (FCh)
       'STANDBY' : 0xFD,    # Begin Standby Mode 1111   1101 (FDh)
       'RESET' : 0xFE,      # Reset to Power-Up Values 1111   1110 (FEh)
      }
      
def digital_write(pin, value):
    GPIO.output(pin, value)

def digital_read(pin):
    return GPIO.input(pin)

def delay_ms(delaytime):
    time.sleep(delaytime // 1000.0)

class ADS1256:
    def __init__(self):
        self.rst_pin = RST_PIN
        self.cs_pin = CS_PIN
        self.drdy_pin = DRDY_PIN
        self.mode=0
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(RST_PIN, GPIO.OUT)
        GPIO.setup(CS_PIN, GPIO.OUT)
        GPIO.setup(DRDY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        spi.max_speed_hz = 2000000
        spi.mode = 0b01
        
    def reset(self):
        digital_write(self.rst_pin, GPIO.HIGH)
        delay_ms(200)
        digital_write(self.rst_pin, GPIO.LOW)
        delay_ms(200)
        digital_write(self.rst_pin, GPIO.HIGH)
        
    def sleep(self):
        digital_write(self.rst_pin, GPIO.LOW)
        delay_ms(200)
    
    def writeCmd(self, reg):
        digital_write(self.cs_pin, GPIO.LOW)
        spi.writebytes([reg])
        digital_write(self.cs_pin, GPIO.HIGH)
    
    def writeReg(self, reg, data):
        digital_write(self.cs_pin, GPIO.LOW)
        spi.writebytes([CMD['WREG'] | reg, 0x00, data])
        digital_write(self.cs_pin, GPIO.HIGH)
        
    def readData(self, reg):
        digital_write(self.cs_pin, GPIO.LOW)
        spi.writebytes([CMD['RREG'] | reg, 0x00])
        data = spi.readbytes(1)
        digital_write(self.cs_pin, GPIO.HIGH)

        return data
        
    def waitDRDY(self):
        for i in range(400000):
            if(digital_read(self.drdy_pin) == 0):
                break
                
        if(i >= 400000):
            print ("#Time Out ...\n")
        
        
    def readChipID(self):
        self.waitDRDY()
        id = self.readData(REG_E['STATUS'])
        id = id[0] >> 4
        return id
        
    def configADC(self, gain, drate):
        
        self.waitDRDY()
        digital_write(self.cs_pin, GPIO.LOW)
        delay_ms(10)
        
        # 0. reset
        spi.writebytes([0xFE]) 
        
        # 1. status byte/config
        spi.writebytes([CMD['WREG']|REG_E['STATUS'], 0x00, 0x01])
        
        # 2. gain setting
        spi.writebytes([CMD['WREG']|REG_E['ADCON'], 0x00, 0x20|gain])
        
        # 2. datarate setting
        spi.writebytes([CMD['WREG']|REG_E['DRATE'], 0x00, drate])
        delay_ms(1)
        
        digital_write(self.cs_pin, GPIO.HIGH)
        delay_ms(1) 

    def setChannel(self, chan):
        if channel > 7:
            return 0
        
        self.writeReg(REG_E['MUX'], (chan<<4) | (1<<3))

    def setDiffChannel(self, chan):
        if chan == 0:
            self.writeReg(REG_E['MUX'], 0x01)
        elif chan == 1:
            self.writeReg(REG_E['MUX'], 0x23)
        elif chan == 2:
            self.writeReg(REG_E['MUX'], 0x45)
        elif chan == 3:
            self.writeReg(REG_E['MUX'], 0x67)

    def setMode(self, Mode):
        self.mode = Mode

    def initADC(self, gain, drate):
        self.reset()
        id = self.readChipID()

        if id != 3 :
            print("#ID Read failed   ")
            return -1
            
        self.configADC(gain, drate)
        return 0
        
    def readADC(self):
        self.waitDRDY()
        digital_write(self.cs_pin, GPIO.LOW)
        spi.writebytes([CMD['RDATA']])

        buf = spi.readbytes(3)
        digital_write(self.cs_pin, GPIO.HIGH)
        read = (buf[0]<<16) & 0xff0000
        read |= (buf[1]<<8) & 0xff00
        read |= (buf[2]) & 0xff
        
        if (read & 0x800000) != 0: # two's complement
            read-=1<<24
            
        return read
 
    def getValue(self, Channel):
        # 0 Single-ended input  8 channel
        # 1 Differential input  4 channel
        if(self.mode == 0):
            if(Channel>=8):
                return 0
                
            self.waitDRDY()
            self.setChannel(Channel)
            self.writeCmd(CMD['SYNC'])
            self.writeCmd(CMD['WAKEUP'])
            v = self.readADC()
        else:
            if(Channel>=4):
                return 0
            
            self.waitDRDY()
            self.setDiffChannel(Channel)
            self.writeCmd(CMD['SYNC'])
            self.writeCmd(CMD['WAKEUP']) 
            v = self.readADC()
        return v

    def calibrate():
        # TODO
        pass
