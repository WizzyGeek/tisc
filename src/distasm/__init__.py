from os import PathLike
from tasmc.consts import REG_NAMES

IDX2REG = [""] * 8

for k, v in REG_NAMES.items():
    IDX2REG[v] = k

OV2JMP = ("jmp", "jz", "jc")
OV2ALU = ("add", "sub", "nand", "copy")

def mem_from_file(fp: PathLike | str | bytes) -> bytearray:
    fd = open(fp, "rb")
    m = fd.read()
    b = bytearray(256 * 256) # addresses given by 16 bits
    b[:len(m)] = m
    return b

class Instruction:
    def __init__(self, name: str, args: list[str]):
        self.name = name
        self.args = args

    def __str__(self):
        return f"{self.name} {', '.join(str(i) for i in self.args)}"

def disasseble_gen_(src: bytes | bytearray):
    idx = 0
    while idx < len(src):
        inst = src[idx]

        op = (inst & 0xc0) >> 6
        if op == 0b10: #movx
            a = (inst & 0b111)
            b = (inst >> 3) & 0b111
            yield Instruction("movx", [IDX2REG[a], IDX2REG[b]])
        elif op == 0b00: # JUMPS
            a = (inst >> 4) & 3
            if inst == 15: # HLT
                yield Instruction("hlt", [])
            elif not inst & 2: # NOP
                yield Instruction("nop", [])
            elif (a == 0) or (a == 1) or (a == 2): # jz, jc, jmp
                num = int.from_bytes(src[idx+1:idx+3], "little", signed=True)
                yield Instruction(OV2JMP[a], [str(num)])
                idx += 2
        elif op == 1: # ALU
            a = (inst >> 2) & 3
            ov = (inst >> 4) & 3                      # b
            yield Instruction(OV2ALU[ov], [IDX2REG[a], IDX2REG[inst & 3]])
        elif op == 3:
            ov = (inst >> 5) & 1
            a = (inst >> 2) & 0b111
            r = inst & 1
            if (inst >> 1) & 1:
                # this Has to be rload or load imm. rn
                idx += 1
                yield Instruction(("rloadi", "loadi")[r], [IDX2REG[a], str(src[idx])])
            else:
                yield Instruction("r" * (not r) + ("loadrl", "storerl")[ov], [IDX2REG[a]])

        idx += 1

def disassemble(src: bytes | bytearray):
    return "\n".join(map(str, disasseble_gen_(src)))