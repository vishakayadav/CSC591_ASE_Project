import os.path
import re
import sys

from src.study.hbo import HBO
from tabulate import tabulate

from src.comparison_stats import bootstrap, cliffs_delta, ScottKnott, kruskal_wallis_stats
from src.contrast_set import xpln, selects, decision_tree
from src.data import DATA
from src.utils import coerce, help_string, result_table, comparisons, get_mean_result, create_preprocessed_csv, the


def settings(pstr):
    table = {}
    pattern = """\n[\s]+[-][\S]+[\s]+[-][-]([\S]+)[^\n]+= ([\S]+)"""
    r = re.compile(pattern)
    matches = r.findall(pstr)
    for k, v in matches:
        table[k] = coerce(v)
    return table


def cli(options):
    """
    Parses the help string to extract a table of options and sets the inner dictionary values
    :param options: String of settings
    """
    for key, val in options.items():
        val = str(val)
        for n, x in enumerate(sys.argv):
            if x == "-" + key[0] or x == "--" + key:
                if val.lower() == "false":
                    val = "true"
                elif val.lower() == "true":
                    val = "false"
                else:
                    val = sys.argv[n + 1]
                # val = val == "false" and "true" or val == "true" and "false" or sys.argv[n+1]
        options[key] = coerce(val)
    return options


def main():
    saved, fails, options = {}, 0, the
    for key, val in cli(settings(help_string)).items():
        options[key] = val
        saved[key] = val

    if options["help"]:
        print(help_string)
    else:
        no_of_evals = {"all": 0, "sway1": 0, "sway2": 0, "sway3": 0, "xpln1": 0, "xpln2": 0, "xpln3": 0, "top": 0}
        ranks = {"all": 0, "sway1": 0, "sway2": 0, "sway3": 0, "xpln1": 0, "xpln2": 0, "xpln3": 0, "top": 0}

        count = 0
        create_preprocessed_csv(options["file"])
        data = DATA(options["file"])  # read in the data to get "all" result
        data = DATA(os.path.join(os.path.dirname(options["file"]), "processed", os.path.basename(options["file"])))
        best_params, hpo_evals = HBO().hpo_hyperopt_params()

        # normalize the rank of rows from 1-100 where ranking is done on the basis of zitzler predicate
        total_rows = len(data.rows)
        for i, row in enumerate(data.betters(total_rows)[0]):
            row.rank = 1 + (i/total_rows)*99

        while count < options["niter"]:
            best, rest, evals = data.sway()  # get the "sway1" results
            rule, _ = xpln(data, best, rest)  # get the "xpln1" results

            best2, rest2, evals2 = data.sway2(best_params, hpo_evals)  # get the "sway2" results
            best_xpln2, rest_xpln2 = decision_tree(data, best2, rest2)  # get the "xpln3" results

            best3, rest3, evals3 = data.sway3()  # get the "sway3" results
            best_xpln3, rest_xpln3 = decision_tree(data, best3, rest3)  # get the "xpln3" results

            # if rule is present
            if rule:
                # store best data for each algo
                xpln1 = DATA(data, selects(rule, data.rows))
                xpln2 = DATA(data, best_xpln2)
                xpln3 = DATA(data, best_xpln3)

                top, _ = data.betters(len(best.rows))
                top = DATA(data, top)

                result_table['all'].append(data)
                result_table['sway1'].append(best)
                result_table['sway2'].append(best2)
                result_table['sway3'].append(best3)
                result_table['xpln1'].append(xpln1)
                result_table['xpln2'].append(xpln2)
                result_table['xpln3'].append(xpln3)
                result_table['top'].append(top)

                ranks['all'] += sum([r.rank for r in data.rows]) // len(data.rows)
                ranks['sway1'] += sum([r.rank for r in best.rows]) // len(best.rows)
                ranks['sway2'] += sum([r.rank for r in best2.rows]) // len(best2.rows)
                ranks['sway3'] += sum([r.rank for r in best3.rows]) // len(best3.rows)
                ranks['xpln1'] += sum([r.rank for r in xpln1.rows]) // len(xpln1.rows)
                ranks['xpln2'] += sum([r.rank for r in xpln2.rows]) // len(xpln2.rows)
                ranks['xpln3'] += sum([r.rank for r in xpln3.rows]) // len(xpln3.rows)
                ranks['top'] += sum([r.rank for r in top.rows]) // len(top.rows)

                no_of_evals["all"] += 0
                no_of_evals["sway1"] += evals
                no_of_evals["sway2"] += evals2
                no_of_evals["sway3"] += evals3
                no_of_evals["xpln1"] += evals
                no_of_evals["xpln2"] += evals2
                no_of_evals["xpln3"] += evals3
                no_of_evals["top"] += len(data.rows)

                for i in range(len(comparisons)):
                    (base, diff), result = comparisons[i]

                    if result is None:
                        comparisons[i][1] = ["=" for _ in range(len(data.cols.y))]  # initialize with '='

                    for k in range(len(data.cols.y)):
                        if comparisons[i][1][k] == "=":
                            base_y = result_table[base][count].cols.y[k]
                            diff_y = result_table[diff][count].cols.y[k]
                            equals = bootstrap(base_y.vals(), diff_y.vals()) and \
                                     cliffs_delta(base_y.vals(), diff_y.vals())

                            if not equals:
                                if base == diff:  # when comparing same algo on same data should never fail
                                    print(f"WARNING: {base} to {diff} comparison failed for {k}")
                                    print(f"""Preview: {result_table[base][count].cols.y[k].txt}""")

                                comparisons[i][1][k] = "≠"
                count += 1

        # generate the stats table
        headers = [y.txt for y in data.cols.y]
        data_table = []
        sknott = ScottKnott()
        stats = {}

        for k, v in result_table.items():
            new_k = k.replace("sway2", "sway2 (hpo)").replace("sway3", "sway3 (kmeans)") \
                .replace("xpln2", "xpln2 (hpo & dtree)").replace("xpln3", "xpln3 (kmeans & dtree)")
            stats[k] = get_mean_result(v)
            stats_list = [new_k] + [stats[k][y] for y in headers]
            stats_list += [no_of_evals[k] // options["niter"]]   # add avg number of evals
            stats_list += [ranks[k] // options["niter"]]         # add avg rank of rows
            data_table.append(stats_list)
            if k not in ["all", "top"]:
                sknott.rxs.append(sknott.RX(list(stats[k].values()), k))

        print(tabulate(data_table, headers=headers + ["Evals", "Rank"], numalign="right"))
        print()

        comparison_table = []
        for [base, diff], result in comparisons:
            comparison_table.append([f"{base} to {diff}"] + result)
        print(tabulate(comparison_table, headers=headers, numalign="right"))

        print("\n\nKruskal-Wallis Statistical Evaluation on the above Algos")
        kw_table = []
        kw_sways, kw_xplns = kruskal_wallis_stats(data, result_table, stats, )
        kw_table.append(["Best Sways"] + kw_sways)
        kw_table.append(["Best Xplns"] + kw_xplns)
        print(tabulate(kw_table, headers=headers, numalign="right"))

        print("\n\nScottKnott Ranking")
        sknott.scott_knot()
        sknott.tiles()
        for rx in sknott.rxs:
            print(rx["name"], rx["rank"], rx["show"])

    sys.exit(fails)


if __name__ == "__main__":
    main()
