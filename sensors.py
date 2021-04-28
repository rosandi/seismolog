#!/usr/bin/python3

from ina219 import INA219

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 1.0
BUS=2

class pvsense:
    ina=None
    
    def __init__(self):
        self.ina=INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, BUS)
        self.ina.configure(self.ina.RANGE_32V,self.ina.GAIN_AUTO)

    def read(self):
        v = {
            'voltage': self.ina.voltage(),
            'current': self.ina.current(),
            'supply': self.ina.supply_voltage(),
            'shunt': self.ina.shunt_voltage(),
            'power': self.ina.power()
            }
        return v

if __name__ == "__main__":
    pv = pvsense().read()

    print("Bus Voltage    : %.3f V" % pv['voltage'])
    print("Bus Current    : %.3f mA" % pv['current'])
    print("Supply Voltage : %.3f V" % pv['supply'])
    print("Shunt voltage  : %.3f mV" % pv['shunt'])
    print("Power          : %.3f mW" % pv['power'])
