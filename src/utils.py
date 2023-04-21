import math
import os
import random
from copy import deepcopy
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from src import settings

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


def per(t, p):
    """
    Returns value of t at pth position,
    where p is calculated using the given value and the length of t
    """
    p = math.floor(((p or 0.5) * len(t)) + 0.5)
    return t[max(0, min(len(t), p) - 1)]


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
    for digit in [int, float]:
        try:
            return digit(s)
        except ValueError:
            pass
    if s.lower() == "true":
        return True
    if s.lower() == "false":
        return False
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


def create_preprocessed_csv(file_path):
    """
    Fills the missing values in the dataframe,
    Applies label encoding to the categorical columns, and
    Saves the preprocessed dataframe to a new CSV file
    """
    df = pd.read_csv(file_path)
    df = fill_missing_values(df)
    columns = df.columns
    syms = [col for col in columns if col.strip()[0].islower() and df[col].dtype == 'O']
    for sym in syms:
        df[sym] = LabelEncoder().fit_transform(df[sym].astype(str))
    preprocessed_file_path = os.path.join(os.path.dirname(file_path), "processed", os.path.basename(file_path))
    df.to_csv(preprocessed_file_path, index=False)


def fill_missing_values(df):
    """
    Fills missing values with column means
    Replace '?' with NaN, convert to float, and impute with column means
    """
    missing_cols = df.columns[df.isnull().any(axis=0)]
    for col in missing_cols:
        df[col].fillna(df[col].mean(), inplace=True)

    missing_cols = df.columns[df.eq('?').any()]
    for col in missing_cols:
        df[col] = df[col].replace('?', np.nan).astype(float)
        df[col].fillna(df[col].mean(), inplace=True)
    return df


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


def get_mean_result(data_array):
    mean_res = {}
    for data in data_array:
        for k, v in data.stats().items():
            mean_res[k] = mean_res.get(k, 0) + v
    for k, v in mean_res.items():
        mean_res[k] /= the['niter']
    return mean_res


# Test Engine util function
def example(key: str, text: str, fun) -> None:
    """
    Update the help string with actions passed as key, text and func
    """
    example_funcs[key] = fun
    global help_string
    help_string = f"""{help_string} -g {key} \t {text} \n"""
