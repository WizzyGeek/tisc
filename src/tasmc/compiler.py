from __future__ import annotations
from typing import Iterable
from collections import defaultdict

from .bitfield import Bits
from .insts import JMP
from .tokens import LabelToken, JMPToken


M = ((1 << 16) - 1)

def compile(toks: Iterable[bytes | Bits | JMPToken | LabelToken]) -> bytes:
    w_mem = bytearray()
    label_locations: dict[str, int] = {} # store byte index of label
    label_idx_map: dict[str, list[int]] = defaultdict(list) # label: idx, change w_mem[idx:idx+2]

    byteindex = 0
    for tok in toks:
        if isinstance(tok, (bytes, Bits)):
            byteindex += len(tok)
            w_mem.extend(bytes(tok))
        elif isinstance(tok, LabelToken):
            label_locations[tok.name] = (byteindex - 1) & M
        elif isinstance(tok, JMPToken):
            i = JMP(variant=tok.inst)
            if (k := label_locations.get(tok.label)) is not None:
                i.offset = (k - (byteindex + 2)) & M # tested, ends up one byte before
            else:
                label_idx_map[tok.label].append(byteindex + 1)
            w_mem.extend(i.to_bytes(3, "little"))
            byteindex += 3

    for lbl, idxs in label_idx_map.items():
        if (k:=label_locations.get(lbl)) is not None:
            for idx in idxs:
                w_mem[idx:idx+2] = ((k - (idx + 1)) & M).to_bytes(2, "little")
        else:
            pass # ehe
    return w_mem