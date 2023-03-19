# Refernce emulator, to be made in C++
import numpy as np

class PCwrapper:
    def __init__(self, arr, emu):
        self.arr = arr
        self.emu = emu

    def __setitem__(self, k, v):
        if k == 0b110:
            self.emu.pc = self.emu.pc >> 8 << 8 | (v & 255)
            return
        if k == 0b111:
            self.emu.pc = ((v & 255) << 8) | (self.emu.pc & 255)
            return
        self.arr[k] = v

    def __getitem__(self, k):
        if k == 0b110 :
            return self.emu.pc & 255
        if k == 0b111:
            return self.emu.pc >> 8
        return self.arr[k]

class Halt(Exception):
    """An exception to signal halting"""

class Emulator:
    def __init__(self, program_mem, probe = None) -> None:
        self.mem = np.zeros(256 * 256, dtype=np.uint8)
        self.rom = program_mem # strict mode, no writes
        self.registers = np.zeros(6, dtype=np.uint8)
        self.carry = False
        self.zero = False
        self.pc = 0 # speed up Instruction access
        # 16 bit adds and 8 bit splits consume more code in python
        # in c++ a benchmark maybe needed
        self._pcwrapper = PCwrapper(self.registers, self) # Preserve compat at cost of speed
        self.probe = probe

    def execute_one(self, inst): # pc is beyond current byte while entering
        # but pc is below next address by 1 while exiting
        op = (inst & 0xc0) >> 6
        if op == 0b10: #movx
            a = (inst & 0b111)
            b = (inst >> 3) & 0b111
            if (a >> 1) == 0b11 or (b >> 1) == 0b11:
                self._pcwrapper[a], self._pcwrapper[b] = self._pcwrapper[b], self._pcwrapper[a]
                return
            self.registers[a], self.registers[b] = self.registers[b], self.registers[a]
            return
        if op == 0b00: # JUMPS
            if inst == 15: # HLT
                raise Halt()
            if not inst & 2: # NOP
                return
            a = (inst >> 4) & 3
            if (a == 0) or (a == 1 and self.zero) or (a == 2 and self.carry): # jz, jc, jmp
                self.pc += ((self.rom[self.pc + 1] << 8) | (self.rom[self.pc]))
            self.pc += 1
            return
        if op == 1: # ALU
            a = (inst >> 2) & 3
            ov = (inst >> 4) & 3
            if ov == 2: # nand
                b = ~(self.registers[a] & self.registers[inst & 0b11])
            elif ov == 0 or ov == 1: # add, sub
                b = self.registers[a] + self.registers[inst & 0b11]
            else: # copy
                b = self.registers[inst & 0b11]
            self.registers[a] = ov = b & 255 # reuse variable
            self.carry = bool(b >> 8)
            self.zero = (ov == 0)
            return
        if op == 3:
            ov = (inst >> 5) & 1
            a = (inst >> 2) & 0b111
            if (inst >> 1) & 1:
                # this Has to be rload or load imm rn
                self._pcwrapper[a] = self.mem[self.pc] if inst & 1 else self.rom[self.pc]
                return
            tmp = self.registers[0b100] | (self.registers[0b101] << 8)
            if ov == 0:
                self._pcwrapper[a] = self.mem[tmp] if inst & 1 else self.rom[tmp]
                return
            (self.mem if inst & 1 else self.rom)[tmp] = self._pcwrapper[a]

    @staticmethod
    def get_signed_value(val):
        return val.astype(np.int8)

    def execute(self):
        if callable(self.probe):
            while True:
                try:
                    i = self.rom[self.pc]
                except IndexError:
                    self.pc = 0
                    print("Reached end of program_mem without HALT")
                    if input("Loop back to first instruction? (Y/n)")[0].lower() == "n":
                        break
                    i = self.rom[0]
                except KeyError:
                    print("KeyError at index", self.pc, "using default value 0")
                    i = 0
                self.pc += 1
                print("-" * 4, "\n", "Executing Instruction: ", bin(i)[2:].rjust(8, "0"))
                try:
                    self.execute_one(i)
                except Halt:
                    print("HALT")
                    break
                self.probe(self)
        else:
            while True:
                try:
                    i = self.rom[self.pc]
                except IndexError:
                    self.pc = 0
                    print("Reached end of program_mem without HALT")
                    if input("Loop back to first instruction? (Y/n)")[0].lower() == "n":
                        break
                    i = self.rom[self.pc]
                except KeyError:
                    print("KeyError at index", self.pc, "using default value 0")
                    i = 0
                self.pc += 1
                try:
                    self.execute_one(i)
                except Halt:
                    break

if __name__ == "__main__":
    e = Emulator({idx: i for idx, i in enumerate([
         0b110_000_10, 0xaf,              #LOAD Immediate x(000) = 0xaf
         0b110_100_10, 0x80,              # LOAD rl(100) = 0x80
         0b11_1_000_00,                   # STORE x at whatever location (rh, rl) describes
         0b10_000_001,                    # swap y(001) and x(000)
         0b110_000_10, 0x01,              # Load immediate x(000) = 0x01
         0b0100_0100,                     # x(000) = x(000) + y(001) (btw this == 176)
         0b0000_0010, 0x03, 0x00,         # JMP +3 bytes
         0b111_000_10, 0b0000_1010, 0x00, # Random bytes
         0b00001111                       # Halt
    ])}, lambda s: print(s.rom, s.registers[4:6])
    )
    print(e.rom)
    e.execute()