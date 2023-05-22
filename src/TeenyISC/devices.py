from __future__ import annotations

from collections import namedtuple
from contextlib import contextmanager
from typing import Any, Callable

Interval = namedtuple("Interval", "start stop")
HIGH_IMPEDANCE = -1

class Device:
    address_range: Interval
    bus: Bus

    def __init__(self, address_range: Interval, bus: Bus):
        self.address_range = address_range
        if self.address_range.start >= self.address_range.stop:
            raise ValueError(f"Invalid address range for device: {address_range}")
        if self.address_range.stop > bus.max_address + 1:
            raise ValueError(f"Address range {address_range} exceeds maximum address of bus {bus}: {bus.max_address}")
        if self.address_range.start < 0:
            raise ValueError("Negative address range {address_range}")
        self.bus = bus
        bus.add_device(self)

    # update internal state based on bus state
    def update(self) -> int: return HIGH_IMPEDANCE # Verilog Equivalent to Z

# Represents a Combinational Circuit connected to Address Bits and Data bits, Read/Write Pin
# Which can select devices based on address ranges
class BusState:
    __slots__ = ("enabled", "reading", "data", "address")
    enabled: bool
    reading: bool
    data: int
    address: int

    @property
    def writing(self): return not self.reading

# NOTE: uses Insertion Sort, linear search, definetly not meant for len(devices) > 10k
# Think around maximum 10
# Alternative is B-Tree, but fack such intresting stuff only hurts performance here
class Bus:
    devices: list[Device]
    state: BusState
    state_subscribers: list[Callable[[Bus], Any]]

    def __init__(self, bits: int):
        self.devices = list()
        self.state = BusState()
        self.state_subscribers = list()
        self.__write_out = False
        self.__out = 0
        self.max_address = (1 << bits) - 1

    def add_state_listener(self, fn: Callable[[Bus], Any]):
        self.state_subscribers.append(fn)

    def dispatch_listeners(self): # loggers, visualisations etc.
        errors = []
        for fn in self.state_subscribers:
            try:
                fn(self)
            except Exception as err:
                errors.append(err)
                try:
                    err._bus_listener = fn # type: ignore
                except Exception:
                    pass
        if errors:
            raise ExceptionGroup("Errors occured while dispatching state subscribers", errors)

    def add_device(self, device: Device):
        if not self.devices:
            self.devices.append(device)
        else:
            for idx, dev in enumerate(self.devices):
                if dev.address_range.stop <= device.address_range.start:
                    if idx < len(self.devices) - 1: # Are we not at end?
                        if self.devices[idx + 1].address_range.start < device.address_range.stop: # no, so check next device start
                            continue
                        else:
                            self.devices.insert(idx + 1, device) # let the new device be after "dev" device
                            return
                    else:
                        self.devices.append(device)
                        return
            raise ValueError(f"Conflict of Address for device {device} in bus {self}, no position found")

    def find_device(self, address: int):
        for dev in self.devices:
            if dev.address_range.start <= address < dev.address_range.stop:
                return dev
        return None

    def _update_state(self, reading: bool, data: int, address: int):
        st = self.state
        st.enabled = True
        st.reading = reading
        st.data = data
        st.address = address
        device = self.find_device(address)
        if device is not None:
            out = device.update()
            self.__write_out = True
            self.out = out if isinstance(out, int) else 0
            self.__write_out = False
            # print(reading, data, address, self.out)
        self.dispatch_listeners()

    @property
    def out(self):
        return self.__out

    @out.setter # Subscriber Protection
    def out(self, val: int):
        if self.__write_out:
            self.__out = val
        else:
            raise Exception("Updating attribute Bus.out for object {self} while object is not being updated.")

    @contextmanager
    def updated_state(self, reading: bool, data: int, address: int):
        self._update_state(reading, data, address)
        try:
            yield self
        finally:
            self.state.enabled = False