
class LoggingMemory(dict):
    def __getitem__(self, key):
        try:
            val = super().__getitem__(key)
        except KeyError:
            print("INFO | Undefined address for read", key)
            super().__setitem__(key, 0)
            return 0
        print("ROM Read>", key, val)
        return val

    def __setitem__(self, key, val):
        print("ROM Write!>", key, val)
        super().__setitem__(key, val)
