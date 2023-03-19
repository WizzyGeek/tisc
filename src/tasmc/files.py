
def write_compiled(content: bytes, name):
    with open(name, "wb") as fd:
        fd.write(content)