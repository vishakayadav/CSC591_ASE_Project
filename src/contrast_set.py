from collections.abc import Callable

from sklearn.tree import DecisionTreeClassifier

from src import utils
from src.data import DATA
from src.discretization import bins
from src.rule import RULE


def xpln(data: DATA, best, rest) -> (dict, float):
    tmp = []
    max_sizes = {}

    def v(has: dict) -> float:
        return utils.value(has, len(best.rows), len(rest.rows), "best")

    def score(ranges: list) -> (float, dict):
        rule = RULE().create(ranges, max_sizes)
        if rule:
            bestr = selects(rule, best.rows)
            restr = selects(rule, rest.rows)
            if len(bestr) + len(restr) > 0:
                return v({"best": len(bestr), "rest": len(restr)}), rule
        return None, None

    for ranges in bins(data.cols.x, {"best": best.rows, "rest": rest.rows}):
        max_sizes[ranges[0]["txt"]] = len(ranges)
        for range in ranges:
            tmp.append({"range": range, "max": len(ranges), "val": v(range["y"].has)})
    rule, most = first_n(sorted(tmp, key=lambda k: k["val"], reverse=True), score)
    return rule, most


def first_n(
    sorted_ranges: list, score_fun: Callable[[list], (float, dict)]
) -> (dict, float):

    first = sorted_ranges[0]["val"]

    def useful(range):
        if range["val"] > 0.05 and range["val"] > first / 10:
            return range

    sorted_ranges = [x for x in sorted_ranges if useful(x)]
    most, out = -1, None
    for n in range(1, len(sorted_ranges) + 1):
        slice_range = [x["range"] for x in sorted_ranges[0:n]]
        tmp, rule = score_fun(slice_range)
        if tmp and tmp > most:
            out, most = rule, tmp
    return out, most


def show_rule(rule: dict) -> dict:
    def pretty(range):
        return range["lo"] if range["lo"] == range["hi"] else [range["lo"], range["hi"]]

    def merges(attr, ranges):
        return list(map(pretty, merge(sorted(ranges, key=lambda k: k["lo"])))), attr

    def merge(t0):
        t, j = [], 0
        while j < len(t0):
            left = t0[j]
            if j + 1 < len(t0):
                right = t0[j + 1]
            else:
                right = None
            if right and left["hi"] == right["lo"]:
                left["hi"] = right["hi"]
                j += 1
            t.append({"lo": left["lo"], "hi": left["hi"]})
            j += 1
        return t if len(t0) == len(t) else merge(t)

    return utils.dkap(rule, merges)


def selects(rule: dict, rows: list) -> list:
    def disjunction(ranges, row):
        for range in ranges:
            lo, hi, at = range["lo"], range["hi"], range["at"]
            x = row.cells[at]
            if x == "?":
                return True
            if lo == hi == x:
                return True
            if lo <= x < hi:
                return True
        return False

    def conjunction(row):
        for ranges in rule.values():
            if not disjunction(ranges, row):
                return False
        return True

    def function(r):
        if conjunction(r):
            return r
        else:
            return None

    return list(filter(function, rows))


def decision_tree(data, best, rest):
    """
    Converts the rows of best and rest into feature vectors and class labels,
    Fits a decision tree classifier on the combined training set, and
    Predicts the class labels for each row in the data object ,thereby classifying data into best and rest.
    """
    X_best = [[row.cells[col.at] for col in best.cols.x] for row in best.rows]
    y_best = ["best"] * len(best.rows)
    X_rest = [[row.cells[col.at] for col in rest.cols.x] for row in rest.rows]
    y_rest = ["rest"] * len(rest.rows)
    X_test = [[row.cells[col.at] for col in data.cols.x] for row in data.rows]

    X_train, y_train = X_best + X_rest, y_best + y_rest
    dt = DecisionTreeClassifier(random_state=0)
    dt.fit(X_train, y_train)

    best_preds, rest_preds = [], []
    for i, row in enumerate(X_test):
        pred = dt.predict([row])
        if pred == "best":
            best_preds.append(data.rows[i])
        else:
            rest_preds.append(data.rows[i])
    return best_preds, rest_preds
