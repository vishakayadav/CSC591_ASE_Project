import math
import random

import numpy as np
import pandas as pd

from src.num import NUM
from src.utils import the
from scipy.stats import kruskal


def samples(t: list, n: int = None) -> dict:
    u = {}
    for i in range(1, (n or len(t)) + 1):
        u[i] = t[random.randint(0, len(t) - 1)]
    return u


def delta(i, other):
    e, y, z = 1e-32, i, other
    return abs(y.mu - z.mu) / ((e + y.sd ** 2 / y.n + z.sd ** 2 / z.n) ** .5)


def cliffs_delta(ns1, ns2) -> bool:
    """
    Non-parametric effect-size test M.Hess, J.Kromrey.
    Robust Confidence Intervals for Effect Sizes:
    A Comparative Study of Cohen's d and Cliff's Delta Under Non-normality and Heterogeneous Variances
    American Educational Research Association, San Diego, April 12 - 16, 2004
    0.147=  small, 0.33 =  medium, 0.474 = large; med --> small at .2385
    """
    if len(ns1) > 256:
        ns1 = samples(ns1, 128)
    if len(ns2) > 128:
        ns2 = samples(ns2, 128)

    n, gt, lt = 0, 0, 0
    for x in ns1:
        for y in ns2:
            n += 1
            if x > y:
                gt += 1
            if x < y:
                lt += 1
    return (abs(lt - gt) / n) <= the["cliff"]


def bootstrap(y0: list, z0: list) -> bool:
    x, y, z, yhat, zhat = NUM(), NUM(), NUM(), [], []
    for y1 in y0:
        x.add(y1)
        y.add(y1)
    for z1 in z0:
        x.add(z1)
        z.add(z1)
    for y1 in y0:
        yhat.append(y1 - y.mu + x.mu)
    for z1 in z0:
        zhat.append(z1 - z.mu + x.mu)

    tobs = delta(y, z)
    n = 0
    for _ in range(1, the["bootstrap"] + 1):
        i = NUM()
        other = NUM()
        for y in samples(yhat).values():
            i.add(y)
        for z in samples(zhat).values():
            other.add(z)
        if delta(i, other) > tobs:
            n += 1
    return n / the["bootstrap"] >= the["conf"]


def kruskal_wallis_stats(data, result_table, stats):
    print('KW significance level: ', the["SigLevel"] / 100)
    sways = ['sway1', 'sway2', 'sway3']
    xplns = ['xpln1', 'xpln2', 'xpln3']
    kw_sways, kw_xplns = [], []

    for col in data.cols.y:
        sway_avgs = [stats["sway1"][col.txt], stats["sway2"][col.txt], stats["sway3"][col.txt]]
        xpln_avgs = [stats["xpln1"][col.txt], stats["xpln2"][col.txt], stats["xpln3"][col.txt]]

        if col.w == -1:
            sway_best_avg = min(sway_avgs)
            xpln_best_avg = min(xpln_avgs)
        else:
            sway_best_avg = max(sway_avgs)
            xpln_best_avg = max(xpln_avgs)

        best_sway = sways[sway_avgs.index(sway_best_avg)]
        best_xpln = xplns[xpln_avgs.index(xpln_best_avg)]

        sway1_col = [row.cells[col.at] for best in result_table["sway1"] for row in best.rows]
        sway2_col = [row.cells[col.at] for best in result_table["sway2"] for row in best.rows]
        sway3_col = [row.cells[col.at] for best in result_table["sway3"] for row in best.rows]
        xpln1_col = [row.cells[col.at] for best in result_table["xpln1"] for row in best.rows]
        xpln2_col = [row.cells[col.at] for best in result_table["xpln2"] for row in best.rows]
        xpln3_col = [row.cells[col.at] for best in result_table["xpln3"] for row in best.rows]

        num_groups = len(sways)
        sway_p_values_kruskal = np.zeros((num_groups, num_groups))
        xpln_p_values_kruskal = np.zeros((num_groups, num_groups))

        for i in range(num_groups):
            for j in range(i + 1, num_groups):
                _, sway_p_value_kruskal = kruskal(sway1_col, sway2_col, sway3_col)
                sway_p_values_kruskal[i, j] = sway_p_value_kruskal
                sway_p_values_kruskal[j, i] = sway_p_value_kruskal

                _, xpln_p_value_kruskal = kruskal(xpln1_col, xpln2_col, xpln3_col)
                xpln_p_values_kruskal[i, j] = xpln_p_value_kruskal
                xpln_p_values_kruskal[j, i] = xpln_p_value_kruskal

        sway_krusal_df = pd.DataFrame(sway_p_values_kruskal, index=sways, columns=sways)
        xpln_krusal_df = pd.DataFrame(xpln_p_values_kruskal, index=xplns, columns=xplns)

        sway_kw_sig = set(sway_krusal_df.iloc[list(np.where(sway_krusal_df >= the["SigLevel"])[0])].index)
        xpln_kw_sig = set(xpln_krusal_df.iloc[list(np.where(xpln_krusal_df >= the["SigLevel"])[0])].index)

        if len(sway_kw_sig) == 0:
            kw_sways.append([best_sway])
        else:
            kw_sways.append(list(sway_kw_sig))

        if len(xpln_kw_sig) == 0:
            kw_xplns.append([best_xpln])
        else:
            kw_xplns.append(list(xpln_kw_sig))

    return kw_sways, kw_xplns


class ScottKnott():
    def __init__(self):
        self.rxs = []

    def RX(self, t: list, s: str) -> dict:
        t.sort()
        return {"name": s or "", "rank": 0, "n": len(t), "show": "", "has": t}

    def mid(self, t):
        t = t["has"] if "has" in t else t
        n = (len(t) - 1) // 2
        return (t[n] + t[n + 1]) / 2 if len(t) % 2 == 0 else t[n + 1]

    def div(self, t):
        t = t["has"] if "has" in t else t
        return (t[len(t) * 9 // 10] - t[len(t) * 1 // 10]) / 2.56

    def merge(self, rx1, rx2):
        rx3 = self.RX([], rx1["name"])
        rx3["has"] = rx1["has"] + rx2["has"]
        rx3["has"].sort()
        rx3["n"] = len(rx3["has"])
        return rx3

    def scott_knot(self):
        def merges(i, j):
            out = self.RX([], self.rxs[i]["name"])
            for k in range(i, j + 1):
                out = self.merge(out, self.rxs[j])
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
                        l["n"] * (self.mid(l) - self.mid(b4)) ** 2 + r["n"] * (self.mid(r) - self.mid(b4)) ** 2
                    ) / (l["n"] + r["n"])
                    if now > best:
                        if abs(self.mid(l) - self.mid(r)) >= cohen:
                            cut, best = j, now
            if cut != None and not same(lo, cut, hi):
                rank = recurse(lo, cut, rank) + 1
                rank = recurse(cut + 1, hi, rank)
            else:
                for i in range(lo, hi + 1):
                    self.rxs[i]["rank"] = rank
            return rank

        self.rxs.sort(key=lambda x: self.mid(x))
        cohen = self.div(merges(0, len(self.rxs) - 1)) * the["cohen"]

        recurse(0, len(self.rxs) - 1, 1)

    def tiles(self):
        huge = float("inf")
        lo, hi = huge, float("-inf")
        for rx in self.rxs:
            lo, hi = min(lo, rx["has"][0]), max(hi, rx["has"][len(rx["has"]) - 1])
        for rx in self.rxs:
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
                x.append("%6.2f" % i)
            rx["show"] = "".join(u) + str(x)
