from src import utils, contrast_set
from src.data import DATA
from src.num import NUM
from src.utils import *

n = 0


def test_the():
    oo(the)


def test_copy():
    t1 = {"a": 1, "b": {"c": 2, "d": [3]}}
    t2 = copy(t1)
    t2["b"]["d"][0] = 10000
    print("b4", t1, "\nafter", t2)


def test_rand():
    num1, num2 = NUM(), NUM()
    utils.seed = the["seed"]
    for i in range(1, 11):
        num1.add(rand(0, 1))

    utils.seed = the["seed"]
    for i in range(1, 11):
        num2.add(rand(0, 1))

    m1, m2 = rnd(num1.mid(), 10), rnd(num2.mid(), 10)
    return m1 == m2 and 0.5 == rnd(m1, 1)


def test_some():
    the["Max"] = 32
    num1 = NUM()
    for i in range(1, 1000 + 1):
        num1.add(i)
    print(num1.has)


def test_sym():
    sym = SYM()
    for x in ["a", "a", "a", "a", "b", "b", "c"]:
        sym.add(x)
    print(sym.mid(), rnd(sym.div()))
    return "a" == sym.mid() and 1.38 == rnd(sym.div())


def test_num():
    num = NUM()
    for x in [1, 1, 1, 1, 2, 2, 3]:
        num.add(x)
    return 11 / 7 == num.mid() and 0.787 == rnd(num.div())


def test_nums():
    num1, num2 = NUM(), NUM()
    utils.seed = the["seed"]
    for i in range(1, 10**3 + 1):
        num1.add(rand(0, 1))

    utils.seed = the["seed"]
    for i in range(1, 10**3 + 1):
        num2.add(rand(0, 1) ** 2)

    m1, m2 = rnd(num1.mid(), 1), rnd(num2.mid(), 1)
    d1, d2 = rnd(num1.div(), 1), rnd(num2.div(), 1)
    print(1, m1, d1)
    print(2, m2, d2)
    return 0.5 == m1 and num1.mid() > num2.mid()


def test_csv():
    def func(t):
        global n
        n += len(t)

    csv(the["file"], func)
    return n == 8 * 399


def test_data():
    data = DATA(the["file"])
    col = data.cols.x[1]
    print(col.lo, col.hi, col.mid(), col.div())
    print(data.stats("mid", data.cols.y, 2))
    return (
        len(data.rows) == 398
        and data.cols.y[0].w == -1
        and data.cols.x[1].at == 1
        and len(data.cols.x) == 4
    )


def test_stats():
    data = DATA(the["file"])
    for k, cols in {"y": data.cols.y, "x": data.cols.x}.items():
        print(k, "mid", data.stats("mid", cols, 2))
        print("", "div", data.stats("div", cols, 2))
    return True


def test_clone():
    data1 = DATA(the["file"])
    data2 = data1.clone(data1.rows)
    print(data1.stats("mid", data1.cols.y, 2))
    print(data2.stats("mid", data2.cols.y, 2))
    return (
        len(data1.rows) == len(data2.rows)
        and data1.cols.y[1].w == data2.cols.y[1].w
        and data1.cols.x[1].at == data2.cols.x[1].at
        and len(data1.cols.x) == len(data2.cols.x)
    )


def test_cliffs():
    utils.seed = the["seed"]
    assert not cliffs_delta([8, 7, 6, 2, 5, 8, 7, 3], [8, 7, 6, 2, 5, 8, 7, 3])
    assert cliffs_delta([8, 7, 6, 2, 5, 8, 7, 3], [9, 9, 7, 8, 10, 9, 6])
    t1, t2 = [], []
    for i in range(1, 1000 + 1):
        t1.append(rand(0, 1))

    for i in range(1, 1000 + 1):
        t2.append(rand(0, 1) ** 0.5)

    assert not cliffs_delta(t1, t1)
    assert cliffs_delta(t1, t2)
    diff, j = False, 1.0
    while not diff:

        def temp_func(x):
            return x * j

        t3 = list(map(temp_func, t1))
        diff = cliffs_delta(t1, t3)
        print(">", rnd(j), diff)
        j = j * 1.025


def test_dist():
    data = DATA(the["file"])
    num = NUM()
    for row in data.rows:
        num.add(data.dist(row, data.rows[1]))
    print({"lo": num.lo, "hi": num.hi, "mid": rnd(num.mid()), "div": rnd(num.div())})


def test_around():
    data = DATA(the["file"])
    print(0, "\t", 0, "\t", data.rows[0].cells)
    for n, t in enumerate(data.around(data.rows[0])):
        if ((n + 1) % 50) == 0:
            print(n + 1, "\t", rnd(t["dist"], 2), "\t", t["row"].cells)


def test_half():
    data = DATA(the["file"])
    left, right, A, B, c, _ = data.half()
    print(len(left), len(right))
    l, r = data.clone(left), data.clone(right)
    print("l", l.stats("mid", l.cols.y, 2))
    print("r", r.stats("mid", r.cols.y, 2))


def test_tree():
    data = DATA(the["file"])
    show_tree(data.cluster(), "mid", data.cols.y, 1)
    return True


def test_sway():
    data = DATA(the["file"])
    best, rest, _ = data.sway()
    print("\nall ", data.stats("mid", data.cols.y, 2))
    print("    ", data.stats("div", data.cols.y, 2))
    print("\nbest", best.stats("mid", best.cols.y, 2))
    print("    ", best.stats("div", best.cols.y, 2))
    print("\nrest", rest.stats("mid", rest.cols.y, 2))
    print("    ", rest.stats("div", rest.cols.y, 2))


def test_bins():
    data = DATA(the["file"])
    best, rest, _ = data.sway()
    print("all", "", "", "", {"best": len(best.rows), "rest": len(rest.rows)})

    b4 = None
    for k, t in enumerate(bins(data.cols.x, {"best": best.rows, "rest": rest.rows})):
        for range in t:
            if range["txt"] != b4:
                print("")
            b4 = range["txt"]
            print(
                range["txt"],
                range["lo"],
                range["hi"],
                rnd(value(range["y"].has, len(best.rows), len(rest.rows), "best")),
                range["y"].has,
            )


def test_xpln():
    utils.seed = the["seed"]
    data = DATA(the["file"])
    best, rest, evals = data.sway()
    rule, most = contrast_set.xpln(data, best, rest)
    print("\n-----------\nexplain=", contrast_set.show_rule(rule))
    selects = contrast_set.selects(rule, data.rows)
    data_selects = [s for s in selects if s != None]
    data1 = data.clone(data_selects)
    print(
        "all               ",
        data.stats("mid", data.cols.y, 2),
        data.stats("div", data.cols.y, 2),
    )
    print(
        "sway with",
        evals,
        "evals",
        best.stats("mid", best.cols.y, 2),
        best.stats("div", best.cols.y, 2),
    )
    print(
        "xpln on",
        evals,
        "evals",
        data1.stats("mid", data1.cols.y, 2),
        data1.stats("div", data1.cols.y, 2),
    )
    top, _ = data.betters(len(best.rows))
    top = data.clone(top)
    print(
        "sort with",
        len(data.rows),
        "evals",
        top.stats("mid", top.cols.y, 2),
        top.stats("div", top.cols.y, 2),
    )


def test_cluster():
    data = DATA(the["file"])
    show(data.cluster(), "mid", data.cols.y, 1)


def test_optimize():
    data = DATA(the["file"])
    show(data.sway(), "mid", data.cols.y, 1)


def test_rep_cols():
    t = rep_cols(dofile(the["file"])["cols"], DATA)
    _ = list(map(oo, t.cols.all))
    _ = list(map(oo, t.rows))


def test_synonyms():
    data = DATA(the["file"])
    show(rep_cols(dofile(the["file"])["cols"], DATA).cluster())


def test_rep_rows():
    t = dofile(the["file"])
    rows = rep_rows(t, DATA, transpose(t["cols"]))
    _ = list(map(oo, rows.cols.all))
    _ = list(map(oo, rows.rows))


def test_prototypes():
    t = dofile(the["file"])
    rows = rep_rows(t, DATA, transpose(t["cols"]))
    show(rows.cluster())


def test_position():
    t = dofile(the["file"])
    rows = rep_rows(t, DATA, transpose(t["cols"]))
    rows.cluster()
    rep_place(rows)


def test_every():
    rep_grid(the["file"], DATA)
