from .devices import Bus, Device, HIGH_IMPEDANCE, Interval
from sys import stdout

class SerialConsoleWriter(Device):
    buf: list[int]
    def __init__(self, address: int, bus: Bus):
        super().__init__(Interval(address, address + 1), bus)
        self.buf = list()

    def update(self):
        if self.bus.state.reading:
            return HIGH_IMPEDANCE
        else:
            if self.bus.state.data != HIGH_IMPEDANCE:
                if self.bus.state.data == 4: # ETX
                    stdout.write("".join(chr(i) for i in self.buf))
                    self.buf.clear()
                if self.bus.state.data != 2: # Start of Text
                    self.buf.append(self.bus.state.data & 0xff)
                return 6 # ASCII ACK IG?? I dont have anything better
            return 0x15 # ASCII Neg ACK
