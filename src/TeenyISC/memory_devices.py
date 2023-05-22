from .devices import Bus, Device, HIGH_IMPEDANCE, Interval

class Memory(Device):
    memory: bytearray
    def __init__(self, size: int, address_lower: int, bus: Bus):
        super().__init__(Interval(address_lower, address_lower + size), bus)
        self.memory = bytearray(size)

    def update(self):
        if self.bus.state.reading:
            return self.memory[self.bus.state.address - self.address_range.start]
        else:
            if self.bus.state.data != HIGH_IMPEDANCE:
                self.memory[self.bus.state.address - self.address_range.start] = self.bus.state.data & 0xff
            return HIGH_IMPEDANCE

    @classmethod
    def from_bytes(cls, byte: bytes, address_low: int, bus: Bus):
        self = super().__new__(cls)
        super(Memory, self).__init__(Interval(address_low, address_low + len(byte)), bus)
        self.memory = bytearray(byte)
        return self