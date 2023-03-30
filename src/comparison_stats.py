import random

from src.num import NUM
from src.utils import the


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
