from .bitfield import BitField

JMP = BitField("JMP", 0b00_00_0010,
    offset=(8, 24),
    offset_lsb=(8, 16),
    offset_msb=(16, 24), # last byte
    variant=(4, 6)
)

ALU = BitField("ALU", 0b01 << 6,
    reg_a=(2, 4),
    reg_b=(0, 2),
    variant=(4,6)
)

MOVX = BitField("MOVX", 0b10 << 6,
    reg_a=(0, 3),
    reg_b=(3, 6)
)

IO = BitField("IO", (0b11 << 6) | 1,
    variant=5, # 0 = load, 1 = store
    reg_a=(2, 5),
    vectorised=1,
    r_pin=0 # needs to be explicitly zeroed
) # *sigh* Why don't i just not use the recommended language for a task?
