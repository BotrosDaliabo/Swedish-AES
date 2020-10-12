class MinMaxPair:
    def __init__(self, min: int, max: int):
        self.data = {"min" : min, "max" : max}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]
