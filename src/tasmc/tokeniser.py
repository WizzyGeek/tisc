
import regex as re
from itertools import accumulate, chain

from .tokens import JMPToken, LabelToken
from .consts import ALU_CODE, JMP_CODE, REG_NAMES, STANDARD
from .insts import ALU, JMP, MOVX, IO

# WARNING: When changing pattern ensure you
# update the "number of groups + 1" for that pattern

toks = {
    "LABEL":     (r"(\w+): *", 2), # 3rd

    "BYTES":     (r"\.bytes 0x((?:[a-f\d]{2} ?)+)(?![a-f\d])", 2),
    "HLT":       (r"hlt", 1),
    "NOP":       (r"nop", 1),
    "JMPS":      (r"(j(?:mp|z|c)) +(0(?:o[0-7]+|b[01]+|x[a-f\d]+)|\d+|\w+)", 3), # 3rd
    "ALU":       (r"(add|sub|nand|copy) +([a-z]+) *, *([a-z]+)", 4),
    "MOVX":      (r"movx +([a-z]+) *, *([a-z]+)", 3),
    "LOADRL":    (r"(r?)loadrl +([a-z]+)", 3),
    "LOADI":     (r"loadi +([a-z]+) *, *(0(?:o[0-7]+|b[01]+|x[a-f\d]+)|\d+)", 3),
    "STORERL":   (r"(r?)storerl +([a-z]+)", 3),

    "COMMENT":   (r"[;#].*", 1),
    "NEWLINE":   (r"\n+", 1), # reset state upon encounter
    "WHITESPACE":(r" +", 1), # 2nd maybe ignore, maybe 4th
    "EOF":       (r"$", 1),
    "INVALID":    (r".*", 1)
}
# Grammar
# <LINEBEGIN>[WHITESPACE][LABEL|INSTS][WHITESPACE][COMMENT]<NEWLINE>

tok_group_shift = {
    k: v + 1 for k, v in zip(toks.keys(), chain([0], accumulate(map(lambda v: v[1], toks.values()))))
} # index zero is match

pat = re.compile("|".join(f"(?P<{n}>{p[0]})" for n, p in toks.items()))

# if __name__ == "__main__":
#     print(tok_group_shift)
#     m = pat.finditer(
#     """
#     rloadrl x
#     loadrl y
#     """
#     )

#     from pprint import pprint
#     pprint(list(map(lambda s: (s.lastgroup, s.groups()), m)))

bases = {
    "o": 8,
    "b": 2,
    "x": 16
}

def parse_reg(reg: str): # Intended ValueError, KeyError
    if len(reg) == 1:
        if reg.isdigit():
            return int(reg)
        else:
            return STANDARD[reg]
    if reg[0] == "0" and not reg[1].isdigit():
        return int(reg[2:], base=bases[reg[1]])
    elif reg.isdigit():
        return int(reg)
    else:
        return REG_NAMES[reg]

def parse_int(s: str): # Intended ValueError
    if len(s) <= 1:
        return int(s)
    if s[0] == "0" and not s[1].isdigit():
        return int(s[2:], base=bases[s[1]])
    return int(s)

def parse_bytes(s: str):
    s = "".join(s.split(" "))
    return bytes(int(s[i:i+2], base=16) for i in range(0, len(s), 2))

# Even though ValueError is allowed to rise it wont actually occur


def generate_tokens(src: str):
    lineno = 1
    line_start = 0
    for m in pat.finditer(src):
        lg = m.lastgroup
        if lg is None or lg == "COMMENT" or lg == "WHITESPACE" or lg == "EOF":
            continue
        shift = tok_group_shift[lg]
        if lg == "NEWLINE":
            line_start = m.end()
            lineno += 1
        elif lg == "ALU":
            reg_a = parse_reg(m.group(shift + 2))
            reg_b = parse_reg(m.group(shift + 3))
            if not -1 < reg_a < 4:
                raise ValueError("Invalid Register: " + m.group(shift + 2), lineno, m.start(tok_group_shift[lg] + 2) - line_start)
            if not -1 < reg_b < 4:
                raise ValueError("Invalid Register: " + m.group(shift + 3), lineno, m.start(tok_group_shift[lg] + 3) - line_start)
            yield ALU(variant=ALU_CODE[m.group(shift + 1)], reg_a=reg_a, reg_b=reg_b)
        elif lg == "MOVX":
            reg_a = parse_reg(m.group(shift + 1))
            reg_b = parse_reg(m.group(shift + 2))
            yield MOVX(reg_a=reg_a, reg_b=reg_b)
        elif lg == "JMPS":
            lbl = m.group(shift + 2)
            if (lbl[0] == "0" and len(lbl) > 1 and lbl[2] in bases) or lbl.isdigit():
                yield JMP(variant=JMP_CODE[m.group(shift + 1)], offset=parse_int(lbl))
            else:
                yield JMPToken(lineno=lineno, label=lbl, inst_code=JMP_CODE[m.group(shift + 1)])
        elif lg == "LABEL":
            yield LabelToken(lineno=lineno, name=m.group(shift + 1))
        elif lg == "LOADRL":
            reg_a = parse_reg(m.group(shift + 2))
            if not -1 < reg_a < 8:
                raise ValueError("Invalid Register: " + m.group(shift + 2), lineno, m.start(tok_group_shift[lg] + 2) - line_start)
            yield IO(variant=0, vectorised=0, reg_a=reg_a, r_pin=(m.group(shift+1) == ""))
        elif lg == "LOADI":
            reg_a = parse_reg(m.group(shift + 1))
            if not -1 < reg_a < 8:
                raise ValueError("Invalid Register: " + m.group(shift + 1), lineno, m.start(tok_group_shift[lg] + 2) - line_start)
            yield IO(variant=0, vectorised=1, reg_a=reg_a, r_pin=0)
            yield parse_int(m.group(shift + 2)).to_bytes(1, "little") # OverFlowError, should not occur
        elif lg == "STORERL":
            reg_a = parse_reg(m.group(shift + 2))
            if not -1 < reg_a < 8:
                raise ValueError("Invalid Register: " + m.group(shift + 2), lineno, m.start(tok_group_shift[lg] + 2) - line_start)
            yield IO(variant=1, vectorised=0, reg_a=reg_a, r_pin=(m.group(shift+1) == ""))
        elif lg == "HLT":
            yield b"\x0f"
        elif lg == "NOP":
            yield b"\x00"
        elif lg == "BYTES":
            yield parse_bytes(m.group(shift + 1))
        elif lg == "INVALID":
            raise ValueError(m.group(lg), lineno, m.start(lg) - line_start)