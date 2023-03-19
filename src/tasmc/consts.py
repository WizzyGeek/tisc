
OPCODES = { # Unused
    "JMP": 0b0000 << 4,
    "JZ": 0b0001 << 4,
    "JC": 0b0010 << 4,
    "ADD": 0b0100 << 4,
    "SUB": 0b0101 << 4,
    "NAND": 0b0110 << 4,
    "COPY": 0b0111 << 4,
    "MOVX": 0b10 << 6,
    "LOAD": 0b110 << 5,
    "STORE": 0b111 << 5,
}

REG_NAMES = {
    "x":   0b000, "y":   0b001,
    "z":   0b010, "w":   0b011,

    "rl":  0b100, "rh":  0b101, # Result Low/High
    "ipl": 0b110, "iph": 0b111, # Instruction Pointer Low/High
}

STANDARD = {
    "x":   0b000, "y":   0b001,
    "z":   0b010, "w":   0b011,
}

TASM = {
    "jmp":     0b00_00_0010,
    "jz":      0b00_01_0010,
    "jc":      0b00_10_0010,
    "hlt":     0b00_00_1111, # not an instruction really
    "nop":     0b00_00_0000, # not an instruction

    "add":     0b01_00_00_00,
    "sub":     0b01_01_00_00,
    "nand":    0b01_10_00_00,
    "copy":    0b01_11_00_00,

    "movx":    0b10_000_000,

    "rloadrl": 0b11_0_000_0_0, # Slow realization this isn't RISC AT ALL
    "rstorerl":0b11_1_000_0_0,
    "loadrl":  0b11_0_000_0_1,
    "storerl": 0b11_1_000_0_1,

    "rloadi":  0b11_0_000_1_0,
    # "rstorei": 0b11_1_000_1_0, # Not part of CPU # Future MUL
    "loadi":   0b11_0_000_1_1,
    # "storei":  0b11_1_000_1_1, # not part or CPU # Future DIV
}


# Import into tokens.py
JMP_CODE = {
    "jmp": 0,
    "jz": 1,
    "jc": 2,
}

ALU_CODE = {
    "add": 0,
    "sub": 1,
    "nand": 2,
    "copy": 3,
}