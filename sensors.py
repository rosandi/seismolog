from ina219 import INA219
import json

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 1.0
BUS=2

class photomon:
    ina=None
    
    def __init__(self):
        self.ina=INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, BUS)
        self.ina.configure(pvmon.RANGE_32V,pvmon.GAIN_AUTO)

    def read(self):
        v = {
            'voltage': ina.voltage(),
            'current': ina.current(),
            'supply': ina.supply_voltage(),
            'shunt': ina.shunt_voltage(),
            'power': ina.power()
            }
        return v
