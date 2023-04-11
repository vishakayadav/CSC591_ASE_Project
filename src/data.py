import math
from functools import cmp_to_key
from typing import Union, List, Tuple

from src import utils
from src.cols import COLS
from src.num import NUM
from src.row import ROW
from src.sym import SYM
from src.utils import csv, the, cosine, kap


class DATA:
    def __init__(self, src: Union[str, list, "DATA"] = None, rows: Union[list, ROW] = None) -> None:
        self.rows = []
        self.cols = None

        if src or rows:
            if isinstance(src, str):
                csv(src, self.add)
            else:
                self.cols = COLS(src.cols.names)
                for row in rows:
                    self.add(row)

    def add(self, t: Union[ROW, list]) -> None:
        """
        Adds a new row, updates column headers
        :param t: param t: Union[ROW, list]:
        :return:
        """
        if self.cols:  # true if we have already seen the column names
            t = t if isinstance(t, ROW) else ROW(t)  # t = t if t.cells else ROW(t)
            self.rows.append(t)
            self.cols.add(t)
        else:
            self.cols = COLS(t)  # here, we create "i.cols" from the first row

    def clone(self, init: list = None) -> "DATA":
        """
        Returns a clone with the same structure
        :param init: Initial data for the clone
        :return:
        """
        if init is None:
            init = []

        data = DATA()
        data.add(self.cols.names)

        for _, t in enumerate(init):
            data.add(t)

        return data

    def stats(self, what: str = "mid", cols=None, n_places: int = 0) -> (Union[float, str], str):
        """
        Reports mid or div of cols (defaults to i.cols.y)
        :param what: str: Statistics to collect (Default value = None)
        :param cols: Columns on which statistics is collected (Default value = None)
        :param n_places: int: Decimal places to round (Default value = 0)
        :return: tuple(Union[float, str], str)
        """

        def fun(_, col):
            val = getattr(col, what)()
            return col.rnd(val, n_places), col.txt

        cols = cols or self.cols.y
        tmp = kap(cols, fun)

        # alternative
        # tmp = dict(sorted({col.txt: rnd(getattr(col, what)(), nPlaces) for col in cols or self.cols.y}.items()))

        tmp["N"] = len(self.rows)
        return tmp

    def better_zitzler(self, row1: ROW, row2: ROW) -> bool:
        """
        Returns true if `row1` dominates (via Zitzler04)
        :param row1: ROW
        :param row2: ROW
        :return: bool: true if row1 dominates
        """
        s1, s2 = 0, 0
        ys = self.cols.y
        for col in ys:
            x = col.norm(row1.cells[col.at])
            y = col.norm(row2.cells[col.at])
            s1 = s1 - math.exp(col.w * (x - y) / len(ys))
            s2 = s2 - math.exp(col.w * (y - x) / len(ys))
        return s1 / len(ys) < s2 / len(ys)

    def better_boolean(self, row1: ROW, row2: ROW) -> bool:
        """
        Returns true if `row1` dominates (via Boolean Domination)
        :param row1: ROW
        :param row2: ROW
        :return: bool: true if row1 dominates
        """
        def dominates(row1, row2):
            dominate = False
            for col in self.cols.y:
                x = col.norm(row1.cells[col.at]) * col.w * -1
                y = col.norm(row2.cells[col.at]) * col.w * -1
                if x > y:
                    return False
                elif x < y:
                    dominate = True
            return dominate
        return dominates(row1, row2) and not dominates(row2, row1)

    def dist(self, row1: ROW, row2: ROW, cols: List[Union[NUM, SYM]] = None) -> float:
        """
        Returns distance between the two rows
        :param row1: ROW
        :param row2: ROW
        :param cols: List[Union[NUM, SYM]]
        :return: float: returns 0..1 distance `row1` to `row2`
        """
        n, d = 0, 0
        for col in cols or self.cols.x:
            n += 1
            d += col.dist(row1.cells[col.at], row2.cells[col.at]) ** the["p"]
        return (d / n) ** (1 / the["p"])

    def half(
        self,
        rows: List[ROW] = None,
        cols: List[Union[NUM, SYM]] = None,
        above: ROW = None,
    ) -> (list, list, ROW, ROW, float, int):
        """
        Cluster `rows` into two sets by dividing the data via their distance to two remote points.
        To speed up finding those remote points, only look at `some` of the data.
        Also, to avoid outliers, only look `the.Far=.95` (say) of the way across the space.
        """

        def dist(row1, row2):
            return self.dist(row1, row2, cols)

        def project(row):
            return {"row": row, "dist": cosine(dist(row, A), dist(row, B), c)}

        rows = rows if rows else self.rows
        some = utils.many(rows, the["Halves"])
        A = (the["Reuse"] and above) or utils.any(some)
        tmp = sorted(map(lambda r: {"row": r, "d": dist(r, A)}, some), key=lambda x: x["d"])
        far = tmp[int((len(tmp) - 1) * the['Far'])]
        B = far["row"]
        c = far["d"]
        left = []
        right = []

        for n, tmp in enumerate(sorted(list(map(project, rows)), key=lambda k: k["dist"])):
            if (n + 1) < (len(rows) / 2):
                left.append(tmp["row"])
            else:
                right.append(tmp["row"])

        evals = 1 if the["Reuse"] and above else 2
        return left, right, A, B, c, evals

    def cluster(
        self,
        rows: List[ROW] = None,
        minimum: int = None,
        cols: List[Union[NUM, SYM]] = None,
        above: ROW = None,
    ) -> dict:
        """
        Get `rows` (Cluster) recursively, some `rows` by  dividing them in two, many times
        :param rows:
        :param minimum:
        :param cols:
        :param above:
        :return:
        """
        rows = rows or self.rows
        cols = cols or self.cols.x
        minimum = minimum if minimum else len(rows) ** the["min"]
        node = {"data": self.clone(rows)}

        if len(rows) >= 2 * minimum:
            left, right, node["A"], node["B"], node["c"], _ = self.half(
                rows, cols, above
            )
            node["left"] = self.cluster(left, minimum, cols, node["A"])
            node["right"] = self.cluster(right, minimum, cols, node["B"])
        return node

    def sway(self) -> ("DATA", "DATA", int):
        """
        Recursively prune the worst half the data
        :return: the survivors and some sample of the rest
        """
        data = self

        def worker(rows, worse, evals0=None, above=None):
            if len(rows) <= len(data.rows) ** the["min"]:
                return rows, utils.many(worse, the["rest"] * len(rows)), evals0
            else:
                l, r, A, B, c, evals = self.half(rows=rows, above=above)
                if self.better_zitzler(B, A):
                    l, r, A, B = r, l, B, A
                for row in r:
                    worse.append(row)
                return worker(l, worse, evals + evals0, A)

        best, rest, evals = worker(data.rows, [], 0)
        return self.clone(best), self.clone(rest), evals

    def sway2(self) -> ("DATA", "DATA", int):
        """
        Recursively prune the worst half the data
        :return: the survivors and some sample of the rest
        """
        data = self

        def worker(rows, worse, evals0=None, above=None):
            if len(rows) <= len(data.rows) ** the["min"]:
                return rows, utils.many(worse, the["rest"] * len(rows)), evals0
            else:
                l, r, A, B, c, evals = self.half(rows=rows, above=above)
                if self.better_boolean(B, A):
                    l, r, A, B = r, l, B, A
                for row in r:
                    worse.append(row)
                return worker(l, worse, evals + evals0, A)

        best, rest, evals = worker(data.rows, [], 0)
        return self.clone(best), self.clone(rest), evals

    def betters(self, n: int) -> Union[Tuple[List, List], List]:
        """
        Split the row at the given integer `n`.
        If `n` is not defined return the row list as it is
        :param n: integer number where the list has to be split
        :return: either a list or a tuple of two lists
        """
        tmp = sorted(
            self.rows,
            key=cmp_to_key(lambda row1, row2: -1 if self.better_zitzler(row1, row2) else 1)
        )
        return n and tmp[1:n], tmp[n+1:] or tmp
