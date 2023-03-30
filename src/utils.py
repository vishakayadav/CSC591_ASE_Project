import json
import math
import re
from copy import deepcopy
from pathlib import Path
from typing import Union, List

import settings
from src.range import RANGE
from src.sym import SYM

the = settings.THE
seed = settings.SEED
help_string = settings.HELP
example_funcs = settings.EXAMPLE_FUNCS


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
    x1 = (a**2 + c**2 - b**2) / ((2 * c) or 1)  # might be an issue if c is 0
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
    with open(s_file.absolute(), "r") as file:
        for _, line in enumerate(file):
            row = list(map(coerce, line.strip().split(",")))
            t.append(row)
            func(row)


# Clustering
def show_tree(node, what, cols, n_places, lvl=0):
    """Cluster can be displayed by this function."""
    if node:
        print("|.. " * lvl + "[" + str(len(node["data"].rows)) + "]" + "  ", end="")
        if not node.get("left") or lvl == 0:
            print(node["data"].stats("mid", node["data"].cols.y, n_places))
        else:
            print("")
        show_tree(node.get("left"), what, cols, n_places, lvl + 1)
        show_tree(node.get("right"), what, cols, n_places, lvl + 1)


# Discretization
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
                    k = int(bin(col, x))
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
    return b**2 / (b + r)


def cliffs_delta(ns1, ns2) -> bool:
    """
    Non-parametric effect-size test M.Hess, J.Kromrey.
    Robust Confidence Intervals for Effect Sizes:
    A Comparative Study of Cohen's d and Cliff's Delta Under Non-normality and Heterogeneous Variances
    American Educational Research Association, San Diego, April 12 - 16, 2004
    0.147=  small, 0.33 =  medium, 0.474 = large; med --> small at .2385
    """
    if len(ns1) > 256:
        ns1 = many(ns1, 256)
    if len(ns2) > 256:
        ns2 = many(ns2, 256)
    if len(ns1) > 10 * len(ns2):
        ns1 = many(ns1, 10 * len(ns2))
    if len(ns2) > 10 * len(ns1):
        ns2 = many(ns2, 10 * len(ns1))
    n, gt, lt = 0, 0, 0
    for x in ns1:
        for y in ns2:
            n = n + 1
            if x > y:
                gt = gt + 1
            if x < y:
                lt = lt + 1
    return (abs(lt - gt) / n) > the["cliffs"]


def dofile(file: str) -> dict:
    """
    Loads the file
    :param file: file name to be read
    :return:
    """
    file = open(file, "r", encoding="utf-8")
    text = (
        re.findall(r"(?<=return )[^.]*", file.read())[0]
        .replace("{", "[")
        .replace("}", "]")
        .replace("=", ":")
        .replace("[\n", "{\n")
        .replace(" ]", " }")
        .replace("'", '"')
        .replace("_", '"_"')
    )
    file.close()
    return json.loads(re.sub(r"(\w+):", r'"\1":', text))


# Rep Grid util functions
def rep_cols(cols, data: "DATA") -> "DATA":
    cols = copy(cols)
    for col in cols:
        col[len(col) - 1] = col[0] + ":" + col[len(col) - 1]
        for j in range(1, len(col)):
            col[j - 1] = col[j]
        col.pop()
    first_col = ["Num" + str(k + 1) for k in range(len(cols[0]))]
    cols.insert(0, first_col)
    cols[0][len(cols[0]) - 1] = "thingX"
    return data(cols)


def rep_rows(t, data: "DATA", rows: List["ROW"]) -> "DATA":
    rows = copy(rows)
    for j, s in enumerate(rows[-1]):
        rows[0][j] += ":" + s
    rows.pop()
    for n, row in enumerate(rows):
        if n == 0:
            row.append("thingX")
        else:
            u = t["rows"][-n]
            row.append(u[-1])
    return data(rows)


def rep_place(data: "DATA") -> None:
    n = 20
    g = [[" " for _ in range(n)] for _ in range(n)]
    maxy = 0
    print("")
    for r, row in enumerate(data.rows):
        c = chr(65 + r)
        print(c, row.cells[-1])
        x, y = int(row.x * n // 1), int(row.y * n // 1)
        maxy = int(max(maxy, y + 1))
        g[y][x] = c
    print("")
    for y in range(maxy):
        print(" ".join(g[y]))


def transpose(t):
    u = []
    for i in range(len(t[0])):
        u.append([row[i] for row in t])
    return u


def rep_grid(source_file: str, data: "DATA") -> None:
    t = dofile(source_file)
    rows = rep_rows(t, data, transpose(t["cols"]))
    cols = rep_cols(t["cols"], data)
    show(rows.cluster(), "mid", rows.cols.all, 1)
    show(cols.cluster(), "mid", cols.cols.all, 1)
    rep_place(rows)


def show(
    node,
    what: str = "mid",
    cols: List[Union["Num", "Sym"]] = None,
    n_places: int = 0,
    lvl: int = 0,
) -> None:
    """
    Prints the tree
    :param node: Node of tree
    :param what: str: Statistics to print
    :param cols: list: Columns to print stats for
    :param n_places: int: Number of decimals to round the values to
    :param lvl: int: Level in the tree (default = 0)
    """
    if node:
        print("|.." * lvl, end="")
        if not node.get("left"):
            print(node["data"].rows[-1].cells[-1])
        else:
            print(int(rnd(100 * node["c"], 0)))
        show(node.get("left"), what, cols, n_places, lvl + 1)
        show(node.get("right"), what, cols, n_places, lvl + 1)


# Test Engine util function
def example(key: str, text: str, fun) -> None:
    """
    Update the help string with actions passed as key, text and func
    """
    example_funcs[key] = fun
    global help_string
    help_string = f"""{help_string} -g {key} \t {text} \n"""
