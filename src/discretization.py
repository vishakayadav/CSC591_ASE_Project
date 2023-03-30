import math
from copy import deepcopy

from src.range import RANGE
from src.sym import SYM
from src.utils import the, itself


def bins(cols, rowss):
    """
    Return RANGEs that distinguish sets of rows (stored in `rowss`).
    To reduce the search space, values in `col` are mapped to small number of `bin`s.
    For NUMs, that number is `the.bins=16` (say) (and after dividing the column into, say, 16 bins,
    then we call `mergeAny` to see how many of them can be combined with their neighboring bin).
    """
    out = []
    for col in cols:
        ranges = {}
        for y, rows in rowss.items():
            for row in rows:
                x = row.cells[col.at]
                if x != "?":
                    k = bin(col, x)
                    range = RANGE(col.at, col.txt, x)
                    ranges[k] = ranges[k] if k in ranges else range.get()
                    range.extend(ranges[k], x, y)
        map(itself, ranges)
        ranges = list(dict(sorted(ranges.items())).values())
        out.append(ranges if isinstance(col, SYM) else merge_any(ranges))
    return out


def bin(col, x) -> int:
    """
    Map `x` into a small number of bins. `SYM`s just get mapped to themselves but
    `NUM`s get mapped to one of `the.bins` values.
    Called by function `bins`.
    """
    if x == "?" or isinstance(col, SYM):
        return x
    tmp = (col.hi - col.lo) / (the["bins"] - 1)
    return 1 if col.hi == col.lo else math.floor(float(x) / tmp + 0.5) * tmp


def merge_any(ranges0):
    """
    Given a sorted list of ranges, try fusing adjacent items (stopping when no more fuse-ings can be found).
    When done, make the ranges run from minus to plus infinity (with no gaps in between).
    Called by function `bins`.
    """

    def no_gaps(t):
        if not t:
            return t

        for j in range(1, len(t)):
            t[j]["lo"] = t[j - 1]["hi"]
        t[0]["lo"] = -math.inf
        t[len(t) - 1]["hi"] = math.inf
        return t

    ranges1, j = [], 0
    while j < len(ranges0):
        left = ranges0[j]
        right = None
        try:
            right = ranges0[j + 1]
        except:
            pass
        if right:
            y = merge2(left["y"], right["y"])
            if y:
                j = j + 1
                left["hi"], left["y"] = right["hi"], y
        ranges1.append(left)
        j = j + 1
    return no_gaps(ranges0) if len(ranges0) == len(ranges1) else merge_any(ranges1)


def merge2(col1, col2):
    """
    If the whole is as good (or simpler) than the parts, then return the combination of 2 `col`s.
    Called by function `mergeMany`.
    """
    new = merge(col1, col2)
    if new.div() <= (col1.div() * col1.n + col2.div() * col2.n) / new.n:
        return new


def merge(col1, col2):
    """
    Merge two `cols`. Called by function `merge2`
    """
    new = deepcopy(col1)
    if isinstance(col1, SYM):
        for n in col2.has:
            new.add(n)
    else:
        for n in col2.has:
            new.add(new, n)
        new.lo = min(col1.lo, col2.lo)
        new.hi = max(col1.hi, col2.hi)
    return new
