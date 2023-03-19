import sys
from pathlib import Path

from distasm import disassemble

def main(argv=None):
    argv = argv or sys.argv
    if len(argv) <= 1:
        print("Expected usage: tasmc <filename> [outfile]")
        return
    ifp = Path(argv[1])
    if not ifp.exists():
        print("No file named", ifp, "exists")
        return

    content = disassemble(ifp.open("rb").read())
    sys.stdout.write(content)
    print(end="\n", file=sys.stdout)
    return

if __name__ == "__main__":
    main()