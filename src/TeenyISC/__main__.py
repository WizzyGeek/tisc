import sys

from TeenyISC.mem_reader import mem_from_file
from TeenyISC import TeenyCPU
from TeenyISC.console_writer import SerialConsoleWriter
from TeenyISC.memory_devices import Memory

def main():
    fp = sys.argv[1]
    mem = mem_from_file(fp)
    cpu = TeenyCPU()
    Memory.from_bytes(mem, 0, cpu.bus)          # PROGRAM MEM
    Memory(128 * 256, (1 << 16), cpu.bus)       # RAM
    SerialConsoleWriter((1 << 17) - 1, cpu.bus) # ASCII console interface
    cpu.inst_executor.execute()

if __name__ == "__main__":
    main()