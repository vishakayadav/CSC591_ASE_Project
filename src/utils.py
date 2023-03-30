import math
import random
from copy import deepcopy
from pathlib import Path
from typing import Union

import settings

the = settings.THE
seed = settings.SEED
help_string = settings.HELP
example_funcs = settings.EXAMPLE_FUNCS
result_table = settings.RESULT_TABLE
comparisons = settings.COMPARISONS


# Numeric Operations
def rint(low: int, high: int) -> int:
    """
    Returns an integer between low to high-1
    """
    return math.floor(0.5 + rand(low, high))


def rand(low: int = 0, high: int = 1) -> float:
    global seed
    seed = (16807 * seed) % 2147483647
    return low + (high - low) * seed / 2147483647


def rnd(n: float, n_places: int = 2) -> float:
    """
    Returns `n` rounded to `nPlaces`
    """
    mult = math.pow(10, n_places)
    return math.floor(n * mult + 0.5) / mult


def cosine(a: float, b: float, c: float) -> (float, float):
    """
    Get x, y from a line connecting `a` to `b`
    """
    x1 = (a ** 2 + c ** 2 - b ** 2) / ((2 * c) or 1)  # might be an issue if c is 0
    return x1


# List or Dict Operations
def kap(t: list, func) -> dict:
    """
    Maps `func`(k,v) over list `t` (skip nil results)
    """
    u = {}
    for k, v in enumerate(t):
        v, k = func(k, v)
        # here unlike `#u` in lua that gives the index of last entry, +1 is not required with len(u)
        u[k or len(u)] = v
    return u


def dkap(t: dict, func) -> dict:
    """
    Maps `func`(k,v) over dict `t` (skip nil results)
    """
    u = {}
    for k, v in t.items():
        v, k = func(k, v)
        # here unlike `#u` in lua that gives the index of last entry, +1 is not required with len(u)
        u[k or len(u)] = v
    return u


def keys(t: dict) -> list:
    """
    Returns sorted order of the keys of dict `t`
    """
    return sorted(list(t.keys()))


def push(t: list, x: any) -> any:
    """
    Pushes `x` to end of list `t`
    :return: x
    """
    t.append(x)
    return x


def any(t: list) -> any:
    """
    Returns any one item at random from given list `t`
    """
    return t[rint(0, len(t) - 1)]


def many(t: list, n: int) -> list:
    """
    Returns some items from `t`
    :param t: list
    :param n: integer specifying number of values to be return
    :return: list of `n` random values from list `t`
    """
    u = []
    for _ in range(1, n + 1):
        u.append(any(t))
    return u


def gaussian(mu: float = 0, sd: float = 1) -> float:
    """Returns a sample from a Gaussian with mean `mu` and sd `sd`"""
    r = random.random
    return mu + sd * math.sqrt(-2 * math.log(r())) * math.cos(2 * math.pi * r())


def copy(t: Union[dict, list]) -> Union[dict, list]:
    """Returns deep copy"""
    return deepcopy(t)


# String Operations
def o(t) -> str:
    """
    Returns string representation of `t` where keys are in ascending order.
    """
    t["a"] = t.__class__.__name__
    t["id"] = id(t)
    return dict(sorted(t.items())).__repr__()


def oo(t: any) -> any:
    """
    Prints `t` then return it
    """
    print(o(t))
    return t


def coerce(s: str) -> any:
    """
    Return int or float or bool or string from `s`
    """
    if s.lower() == "true":
        return True
    if s.lower() == "false":
        return False
    if s.isdigit():
        return int(s)
    if s.replace(".", "").isdigit():
        return float(s)
    return s


def csv(s_filename: str, func) -> None:
    """
    Calls `func` on rows (after coercing cell text)
    """
    s_file = Path(s_filename)
    if not s_file.exists():
        print(f"File path {s_file.absolute()} doesn't exist")
        return None
    if not s_file.suffix == ".csv":
        print(f"File {s_file.absolute()} is not CSV type")
        return None

    t = []
    with open(s_file.absolute(), "r", encoding='utf-8') as file:
        for _, line in enumerate(file):
            row = list(map(coerce, line.strip().split(",")))
            t.append(row)
            func(row)


# Miscellaneous Operations
def itself(x: any) -> any:
    """Return self"""
    return x


def value(has: dict, nb: int = 1, nr: int = 1, sgoal=None) -> float:
    """A query that returns the score a distribution of symbols inside a SYM."""
    sgoal = sgoal or True
    b = 0
    r = 0
    for x, n in has.items():
        if x == sgoal:
            b = b + n
        else:
            r = r + n
    b = b / (nb + 1 / math.inf)
    r = r / (nr + 1 / math.inf)
    return b ** 2 / (b + r)


def RX(t: list, s: str) -> dict:
    t.sort()
    return {"name": s or "", "rank": 0, "n": len(t), "show": "", "has": t}


def mid(t):
    t = t["has"] if "has" in t else t
    n = (len(t) - 1) // 2
    return (t[n] + t[n + 1]) / 2 if len(t) % 2 == 0 else t[n + 1]


def div(t):
    t = t["has"] if "has" in t else t
    return (t[len(t) * 9 // 10] - t[len(t) * 1 // 10]) / 2.56


def merge(rx1, rx2):
    rx3 = RX([], rx1["name"])
    rx3["has"] = rx1["has"] + rx2["has"]
    rx3["has"].sort()
    rx3["n"] = len(rx3["has"])
    return rx3


def scott_knot(rxs):
    def merges(i, j):
        out = RX([], rxs[i]["name"])
        for k in range(i, j + 1):
            out = merge(out, rxs[j])
        return out

    def same(lo, cut, hi):
        l = merges(lo, cut)
        r = merges(cut + 1, hi)
        return cliffs_delta(l["has"], r["has"]) and bootstrap(l["has"], r["has"])

    def recurse(lo, hi, rank):
        b4 = merges(lo, hi)
        best = 0
        cut = None
        for j in range(lo, hi + 1):
            if j < hi:
                l = merges(lo, j)
                r = merges(j + 1, hi)
                now = (
                              l["n"] * (mid(l) - mid(b4)) ** 2 + r["n"] * (mid(r) - mid(b4)) ** 2
                      ) / (l["n"] + r["n"])
                if now > best:
                    if abs(mid(l) - mid(r)) >= cohen:
                        cut, best = j, now
        if cut != None and not same(lo, cut, hi):
            rank = recurse(lo, cut, rank) + 1
            rank = recurse(cut + 1, hi, rank)
        else:
            for i in range(lo, hi + 1):
                rxs[i]["rank"] = rank
        return rank

    rxs.sort(key=lambda x: mid(x))
    cohen = div(merges(0, len(rxs) - 1)) * the["cohen"]
    recurse(0, len(rxs) - 1, 1)
    return rxs


def tiles(rxs):
    huge = float("inf")
    lo, hi = huge, float("-inf")
    for rx in rxs:
        lo, hi = min(lo, rx["has"][0]), max(hi, rx["has"][len(rx["has"]) - 1])
    for rx in rxs:
        t, u = rx["has"], []

        def of(x, most):
            return int(max(1, min(most, x)))

        def at(x):
            return t[of(len(t) * x // 1, len(t)) - 1]

        def pos(x):
            return math.floor(
                of(the["width"] * (x - lo) / (hi - lo + 1e-32) // 1, the["width"])
            )

        for i in range(0, the["width"] + 1):
            u.append(" ")
        a, b, c, d, e = at(0.1), at(0.3), at(0.5), at(0.7), at(0.9)
        A, B, C, D, E = pos(a), pos(b), pos(c), pos(d), pos(e)
        for i in range(A, B + 1):
            u[i] = "-"
        for i in range(D, E + 1):
            u[i] = "-"
        u[the["width"] // 2] = "|"
        u[C] = "*"
        x = []
        for i in [a, b, c, d, e]:
            x.append(the["Fmt"] % i)
        rx["show"] = "".join(u) + str(x)
    return rxs


# Test Engine util function
def example(key: str, text: str, fun) -> None:
    """
    Update the help string with actions passed as key, text and func
    """
    example_funcs[key] = fun
    global help_string
    help_string = f"""{help_string} -g {key} \t {text} \n"""
