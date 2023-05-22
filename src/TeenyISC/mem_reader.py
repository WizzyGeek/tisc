from os import PathLike

def mem_from_file(fp: PathLike | str | bytes) -> bytearray:
    fd = open(fp, "rb")
    m = fd.read()
    b = bytearray(256 * 256) # addresses given by 16 bits
    b[:len(m)] = m
    return b

def dict_from_file(fp: PathLike | str | bytes, cls:type[dict]=dict) -> dict:
    fd = open(fp, "rb")
    m = fd.read()
    return cls((idx, val) for idx, val in enumerate(m))

# if __name__ == "__main__":
#     from TeenyISC import TeenyCPU
#     from TeenyISC.util import LoggingMemory
#     t = TeenyCPU(dict_from_file("example_prog.mem", cls=LoggingMemory))
#     t.inst_executor.execute()
#     print(t.program_mem)