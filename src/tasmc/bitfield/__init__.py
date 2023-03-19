
from typing import Literal


def mask(lower, upper): # Slice, 0 indexed, upper limit is strictly exclusive
    return ((1 << upper) - 1) >> lower << lower

def apply_mask(val, lower, upper): # for reads only, returns downshifted
    return (val & mask(lower, upper)) >> lower

# def zero_bits(val, lower, upper):
#     return (~mask(lower, upper)) & val

if True:
    def apply_mask(val, lower, upper): # Optimised, dont care about mask being accurate below lower idx
        # might as well simplify the mask to all high bits
        return (val & ((1 << upper) - 1)) >> lower

class Bits:
    SHIFT_TABLE_POS: tuple[slice, ...] = ()
    SHIFT_TABLE: dict[str, slice] = {}
    DEFAULT: int = 0

    _data: int

    __slots__ = ("_data",)

    def __init__(self, *args, **kwargs):
        self._data = self.DEFAULT

        for i, sl in zip(args, self.SHIFT_TABLE_POS):
            self[sl] = i

        for sl, i in map(lambda s: (self.SHIFT_TABLE[s[0]], s[1]), kwargs.items()):
            self[sl] = i

    def __getitem__(self, idx: int | slice) -> int: # maybe add later: __index__ support, reason left: No benefit
        if isinstance(idx, slice):
            l, h = idx.start, idx.stop
            return apply_mask(self._data, l, h)
        if isinstance(idx, int):
            return (self._data >> idx) & 1
        raise TypeError(f"Expected 'int' or 'slice' instance as subscript, got '{type(idx)}'")

    def __setitem__(self, idx: int | slice, val: int) -> None:
        if isinstance(idx, int):
            self._data = (~(1 << idx) & self._data) | ((val & 1) << idx)
        elif isinstance(idx, slice):
            m = mask(idx.start, idx.stop) # MAYBE OPT: LEFT NOW. REASON: NO SIGNIFICANT BENEFIT
            self._data = (~m & self._data) | (m & (val << idx.start))
        else:
            raise TypeError(f"Expected 'int' or 'slice' instance as subscript, got '{type(idx)}'")

    def __getattr__(self, name: str) -> int:
        try:
            return self[self.SHIFT_TABLE[name]]
        except KeyError:
            raise AttributeError(f"'{name}' is not an attribute of '{type(self)}' object")

    def __setattr__(self, name: str, val) -> None:
        try:
            self[self.SHIFT_TABLE[name]] = val
        except KeyError:
            super().__setattr__(name, val)
            # raise AttributeError(f"'{name}' is not an attribute of '{type(self)}' object")

    def __index__(self) -> int:
        return self._data

    def __bytes__(self) -> bytes:
        return self._data.to_bytes(len(self), 'little')

    def __len__(self):
        q, r = divmod(self._data.bit_length(), 8)
        return q + (r != 0)

    def to_bytes(self, l, byteorder: Literal["big", "little"] = "little"):
        return self._data.to_bytes(l, byteorder)

def BitField(name: str, /, __default: int = 0, **SHIFTS: tuple[int, int] | slice | int) -> type[Bits]:
    """Little Endian Bitfields

    Parameters
    ----------
    name : str
        The name of the bitfield
    __default : int, optional
        An integer describing the default value of the bitfield, by default 0

    Returns
    -------
    type[Bits]
        A new subtype of the Bits class
    """
    tmp = {k: (v if isinstance(v, slice) else (slice(v[0], v[1]) if isinstance(v, tuple) else slice(v, v + 1))) for k, v in SHIFTS.items()}
    at = {
        "DEFAULT": __default,
        "SHIFT_TABLE": tmp,
        "SHIFT_TABLE_POS": tuple(i for i in tmp.values()),
    }
    return type(name, (Bits,), at)

# k = BitField("LOAD", 0b11_0_000_0_0, reg=(2, 5), vectorised=1, r=0)
# inst = k(0b100, 1, 0)
# print(bin(inst._data), bytes(inst))