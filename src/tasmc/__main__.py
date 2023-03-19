from sys import argv
from pathlib import Path
from time import time as t

from tasmc.compiler import compile
from tasmc.tokeniser import generate_tokens as gt
from tasmc.files import write_compiled as wc


def main():
    if len(argv) <= 1:
        print("Expected usage: tasmc <filename> [outfile]")
        return
    ifp = Path(argv[1])
    if not ifp.exists():
        print("No file named", ifp, "exists")
        return
    try:
        ofn = argv[2]
    except IndexError:
        ofn = Path(ifp.stem + ".mem")

    now = t()
    toks = gt(ifp.read_text())
    try:
        wc(compile(toks), ofn)
    except ValueError as err:
        print("Invalid syntax at line", err.args[1], "column", err.args[2] + 1, ":")
        print("   ", err.args[0])
    else:
        print("Done assembling in", t() - now, "seconds")

if __name__ == "__main__":
    main()
