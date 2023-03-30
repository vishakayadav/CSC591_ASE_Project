from src.sym import SYM


class RANGE:
    def __init__(self, at, txt, lo, hi=None):
        self.at = at
        self.txt = txt
        self.lo = lo
        self.hi = lo or hi or lo
        self.y = SYM()

    def get(self) -> dict:
        """Get the range in dict"""
        return {
            "at": self.at,
            "txt": self.txt,
            "lo": self.lo,
            "hi": self.lo or self.hi or self.lo,
            "y": self.y,
        }

    @staticmethod
    def extend(range, n, s) -> dict:
        """Update a RANGE to cover `x` and `y`"""
        range["lo"] = min(n, range["lo"])
        range["hi"] = max(n, range["hi"])
        range["y"].add(s)
        return range
