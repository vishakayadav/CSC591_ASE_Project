from src.data import DATA
from src.utils import the


def ablation_study():
    original_sway()
    sway_without_reuse()
    sway_with_high_halve()
    sway_with_less_min()


def original_sway():
    print("Original Sway")
    data = DATA(the['file'])
    best, rest, _ = data.sway()
    print("\nall ", data.stats('mid', data.cols.y, 2))
    print("    ", data.stats('div', data.cols.y, 2))
    print("\nbest", best.stats('mid', best.cols.y, 2))
    print("    ", best.stats('div', best.cols.y, 2))
    print("\nrest", rest.stats('mid', rest.cols.y, 2))
    print("    ", rest.stats('div', rest.cols.y, 2))


def sway_without_reuse():
    print("Sway with Reuse = False")
    data = DATA(the['file'])
    the["Reuse"] = False
    best, rest, _ = data.sway()
    print("\nall ", data.stats('mid', data.cols.y, 2))
    print("    ", data.stats('div', data.cols.y, 2))
    print("\nbest", best.stats('mid', best.cols.y, 2))
    print("    ", best.stats('div', best.cols.y, 2))
    print("\nrest", rest.stats('mid', rest.cols.y, 2))
    print("    ", rest.stats('div', rest.cols.y, 2))


def sway_with_high_halve():
    print("Sway with Halves increased to 1000")
    data = DATA(the['file'])
    the["Halves"] = 1000
    best, rest, _ = data.sway()
    print("\nall ", data.stats('mid', data.cols.y, 2))
    print("    ", data.stats('div', data.cols.y, 2))
    print("\nbest", best.stats('mid', best.cols.y, 2))
    print("    ", best.stats('div', best.cols.y, 2))
    print("\nrest", rest.stats('mid', rest.cols.y, 2))
    print("    ", rest.stats('div', rest.cols.y, 2))


def sway_with_less_min():
    print("Sway with min reduced to 0.2")
    data = DATA(the['file'])
    the["min"] = 0.2
    best, rest, _ = data.sway()
    print("\nall ", data.stats('mid', data.cols.y, 2))
    print("    ", data.stats('div', data.cols.y, 2))
    print("\nbest", best.stats('mid', best.cols.y, 2))
    print("    ", best.stats('div', best.cols.y, 2))
    print("\nrest", rest.stats('mid', rest.cols.y, 2))
    print("    ", rest.stats('div', rest.cols.y, 2))
