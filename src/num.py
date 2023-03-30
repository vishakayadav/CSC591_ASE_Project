import math
from typing import Union

from src.utils import rnd, the, rint, rand, per


# class num
class NUM:
    # constructor, initialize all variables
    def __init__(self, at: int = 0, txt: str = "", t=None) -> None:
        self.at = at
        self.txt = txt
        self.n = 0
        self.mu = 0
        self.m2 = 0
        self.sd = 0
        self.lo = math.inf
        self.hi = -math.inf
        self.w = -1 if "-" in self.txt else 1
        self.has = {}

        if t:
            for n in t:
                self.add(n)

    def add(self, n: Union[float, str], count: int = 1) -> None:
        """
        Add n and update values required for standard deviation
        :param n: Union[float, str]: Number to add
        :param count: int: number of times to add
        """
        if n != "?":
            self.n += count
            all = len(self.has)

            pos = all + 1 if all < the["Max"] else rint(1, all) if rand() < the["Max"] / self.n else 0

            if pos:
                self.has[pos] = n

            d = n - self.mu
            self.mu += d / self.n
            self.m2 += d * (n - self.mu)
            self.lo = min(n, self.lo)
            self.hi = max(n, self.hi)
            self.sd = 0 if self.n < 2 else (self.m2 / (self.n - 1)) ** .5

    def mid(self) -> float:
        """
        Get mean
        :return: float: mean value
        """
        return per(self.vals(), .5)

    def div(self) -> float:
        """
        Get standard deviation using Welford's Aglorithm
        :return: float: standard deviation
        """
        vals = self.vals()
        return (per(vals, .9) - per(vals, .1)) / 2.58

    @staticmethod
    def rnd(x: Union[float, str], n: int) -> Union[float, str]:
        """
        Get a rounded number if a value else return the str '?'
        :param x: Union[float, str]: number to be rounded
        :param n: int: rounded over to `n` places
        :return: Union[float, str]: rounded value or missing value symbol (?)
        """
        if x == "?":
            return x
        else:
            return rnd(x, n)

    def norm(self, n: Union[float, str]) -> Union[float, str]:
        """
        Get the normalised value of given number
        :param n: float if contains a numeric value else str: `?`
        :return: float: normalised value or return str: `?` as it is
        """
        return n if n == "?" else (n - self.lo) / (self.hi - self.lo + 1e-32)

    def dist(self, n1: Union[float, str], n2: Union[float, str]) -> int:
        """
        Returns distance between the two numbers
        :param n1: float if contains a numeric value else str: `?`
        :param n2: float if contains a numeric value else str: `?`
        :return: int: absolute value of the difference
        """
        if n1 == "?" and n2 == "?":
            return 1
        n1 = self.norm(n1)
        n2 = self.norm(n2)
        if n1 == "?":
            n1 = 1 if n2 < 0.5 else 0
        if n2 == "?":
            n2 = 1 if n1 < 0.5 else 0
        return abs(n1 - n2)

    def vals(self):
        """
        Returns sorted list of column values
        """
        return list(dict(sorted(self.has.items(), key=lambda x: x[1])).values())
