from __future__ import annotations

from typing import Literal

class ALU:
    def __init__(self, cpu: TeenyCPU):
        self.cpu = cpu           # zero, carry
        self.flags: list[bool] = [False, False]

    def nand(self, reg: int, reg2: int): # no, the _tmp is not a temp register, this just python
        _tmp = ~(self.cpu.registers[reg2] & self.cpu.registers[reg])
        self.flags = [False, False]
        if _tmp == 0:
            self.flags[0] = True
        self.cpu.registers[reg] = _tmp

    def add(self, reg: int, reg2: int):
        _tmp = self.cpu.registers[reg2] + self.cpu.registers[reg] # lets not emulate a full adder shall we?
        self.flags = [False, False]
        if _tmp & 0x100:
            self.flags[1] = True
            _tmp = _tmp & 0xff
        if _tmp == 0:
            self.flags[0] = True
        self.cpu.registers[reg] = _tmp

    def sub(self, reg: int, reg2: int): # this one might need a temp register maybe, who knows?
        _tmp = ~self.cpu.registers[reg2] + 1 # 2's complement
        self.flags = [False, False]
        _tmp += self.cpu.registers[reg]
        if _tmp & 0x100:
            self.flags[1] = True
            _tmp &= 0xff
            _tmp = ~_tmp + 1

        if _tmp == 0:
            self.flags[0] = True

        self.cpu.registers[reg] = _tmp

class InstructionExecutor:
    def __init__(self, cpu: TeenyCPU):
        self.cpu = cpu
        self.inst = 0b0000_0000

    def inc_103(self):
        self.cpu.registers[-2:] = ((int.from_bytes(self.cpu.registers[-2:], "little") + 1) & 0xffff).to_bytes(2, "little")

    def fetch_program_byte(self):
        return self.cpu.address_and_data_bus(0, self.cpu.registers[-2], self.cpu.registers[-1])

    def access_register(self, reg: int):
        return self.cpu.registers[reg]

    def _jmp(self):
        # print(0, self.cpu.registers[-2])
        self.inc_103()
        # print(1, self.cpu.registers[-2])
        _tmp = self.fetch_program_byte()
        self.inc_103()
        # print(2, self.cpu.registers[-2])
        self.cpu.registers[-2:] = (((_tmp | self.fetch_program_byte() << 8) + int.from_bytes(self.cpu.registers[-2:], "little")) & 0xffff).to_bytes(2, "little")
        # print(3, self.cpu.registers[-2])

    def execute_cur(self): # Something tells me this is not gonna be easy to make physically, massive/multiple multiplexor
        op = (self.inst & 0b11_00_0000) >> 6
        if op == 0b00: # Does this imply I am gonna need more micro-ops than instructions? I have might have effectively failed at RISC?
            if self.inst & 0b10 == 0: # nop
                return
            ov = self.inst >> 4 & 0b11

            if ov == 00:
                # get data pointed by current 103 register pair (110,111 = P.C program counter) and load into 103 pair
                self._jmp() # jmp
            elif ov == 0b01:
                if self.cpu.alu.flags[0]:
                    self._jmp()
                else:
                    self.inc_103()
                    self.inc_103()
            elif ov == 0b10:
                if self.cpu.alu.flags[1]:
                    self._jmp()
                else:
                    self.inc_103()
                    self.inc_103()
        elif op == 0b01:
            ov = self.inst >> 4 & 0b11 # overloaded op
            i = self.inst & 0b1111
            if ov == 0b00:
                self.cpu.alu.add(i >> 2, i & 0b11)
            elif ov == 0b01:
                self.cpu.alu.sub(i >> 2 & 0b11, i & 0b11)
            elif ov == 0b10:
                self.cpu.alu.nand(i >> 2, i & 0b11)
            else:
                self.cpu.registers[i >> 2] = self.cpu.registers[i & 0b11]
                # self.cpu.simulator_interface("[warn] 4th overload of ALU instruction is undefined")
        elif op == 0b10:
            # yes the temp here needs to a be a temporary register,maybe the alu might benefit too if there is no pipelining
            _tmp = self.access_register(self.inst >> 3 & 0b111)
            self.cpu.registers[self.inst >> 3 & 0b111] = self.access_register(self.inst & 0b111)
            self.cpu.registers[self.inst & 0b111] = _tmp
        elif op == 0b11:
            ov = self.inst >> 5 & 0b01
            r: Literal[0, 1] = self.inst & 1 # type: ignore # select line, rom / ram or acts as 17th bit of address space, active low on ROM
            _tmp = self.inst >> 2 & 0b111
            vec = (self.inst >> 1) & 1 # vector instruction?
            if vec:
                if ov == 0b0:
                    # internal bus in 16 bits?! just maybe we should get 16 bit registers
                    # and we will need 2 multiplexors
                    self.inc_103() # r==1, rloadi is not a thing but keep it
                    self.cpu.registers[_tmp] = self.cpu.address_and_data_bus(r, self.cpu.registers[0b110], self.cpu.registers[0b111])
                elif ov == 0b1: # not real
                    self.cpu.simulator_interface("[warn] Immediate Store instructions not part of TISC v1")
                    self.inc_103()
                    tmp = self.fetch_program_byte()
                    self.inc_103()
                    self.cpu.address_and_data_bus_write(r, tmp, self.fetch_program_byte(), self.cpu.registers[_tmp])
            else:
                if ov == 0b0: # loadrl, rloadrl
                    self.cpu.registers[_tmp] = self.cpu.address_and_data_bus(r, self.cpu.registers[0b100], self.cpu.registers[0b101])
                elif ov == 0b1: # storerl, rstorerl
                    self.cpu.address_and_data_bus_write(r, self.cpu.registers[0b100], self.cpu.registers[0b101], self.cpu.registers[_tmp])


    def execute(self):
        self.inst = self.fetch_program_byte()
        while self.inst != 0b00001111:
            self.execute_cur()
            self.cpu.probe()
            self.inc_103()
            self.inst = self.fetch_program_byte()
        self.cpu.simulator_interface("Halted")

class TeenyCPU: # This simply holds all parts togather, write a similar class
    # for deeper probing
    """A standard TeenyCPU

    This flavor uses the R pin low state to select the rom device
    """
    def __init__(self, program, program_write: Literal[0, 1, 2, 3] = 1):
        if not hasattr(program, "__getitem__"): # Uses memory mapped IO btw
            raise ValueError
        self.registers = memoryview(bytearray(8)) # may swap this too
        self.memory = memoryview(bytearray(256 * 256)) # U may swap this
        self.program_mem = program
        self.alu = ALU(self) # and this
        if not hasattr(program, "__setitem__"):
            self._program_write = 2
        else:
            self._program_write = program_write
        self.inst_executor = InstructionExecutor(self) # I dont see the pont so dont swap this

    def address_and_data_bus(self, select: bool | Literal[0, 1], oct1: int, oct2: int): # 17 bit addressing, basically this is a multiplexor
        i = (oct2 << 8) | oct1
        return self.memory[i] if select else self.program_mem[i]

    def address_and_data_bus_write(self, select: bool | Literal[0, 1], oct1: int, oct2: int, val: int):
        i = (oct2 << 8) | oct1
        if select:
            self.memory[i] = val
        else:
            if self._program_write & 0b01:
                self.simulator_interface("Access Violation, attempt to write to program memory. Strict mode =", self._program_write)
            if self._program_write & 0b10 == 0:
                self.program_mem[i] = val # type: ignore

    def simulator_interface(self, *args):
        print(*args)

    def probe(self):
        if __debug__:
            print("Instruction Executed: ", bin(self.inst_executor.inst)[2:].rjust(8, "0"))
            print("-" * 4)

if __name__ == "__main__":
    from util import LoggingMemory # type: ignore
    mem = LoggingMemory({idx: i for idx, i in enumerate([
         0b110_000_10, 0xaf,              #LOAD Immediate x(000) = 0xaf
         0b110_100_10, 0x80,              # LOAD rl(100) = 0x80
         0b11_1_000_00,                   # STORE x at whatever location (rh, rl) describes
         0b10_000_001,                    # swap y(001) and x(000)
         0b110_000_10, 0x01,              # Load immediate x(000) = 0x01
         0b0100_0100,                     # x(000) = x(000) + y(001) (btw this == 176)
         0b0000_0010, 0x03, 0x00,         # JMP +3 bytes
         0b111_000_10, 0b0000_1010, 0x00, # Random bytes
         0b00001111                       # Halt
    ])})
    print(mem)
    cpu = TeenyCPU(mem)
    cpu.inst_executor.execute()
    print(mem)