import re
import sys

from tabulate import tabulate

from src.comparison_stats import bootstrap, cliffs_delta
from src.contrast_set import xpln, selects
from src.data import DATA
from src.utils import coerce, the, help_string, result_table, comparisons, get_stats


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
        count = 0
        data = DATA(options["file"])  # read in the data to get "all" result
        while count < options["niter"]:
            best, rest, evals = data.sway()  # get the "sway" results
            rule, _ = xpln(data, best, rest)  # get the "xpln" results

            best2, rest2, evals2 = data.sway2()  # get the "sway" results
            rule2, _ = xpln(data, best2, rest2)  # get the "xpln" results

            # if rule is present
            if rule and rule2:
                # store best data for each algo
                top, _ = data.betters(len(best.rows))
                result_table['all']['data'].append(data)
                result_table['sway1']['data'].append(best)
                result_table['sway2']['data'].append(best2)
                result_table['xpln1']['data'].append(DATA(data, selects(rule, data.rows)))
                result_table['xpln2']['data'].append(DATA(data, selects(rule2, data.rows)))
                result_table['top']['data'].append(DATA(data, top))

                # store no. of evaluations for each algo
                result_table['all']['evals'] += 0  # 0 evals to get "all" data
                result_table['sway1']['evals'] += evals  # sway() returns the evals
                result_table['sway2']['evals'] += evals2
                result_table['xpln1']['evals'] += evals  # xpln() uses data from sway so same evals
                result_table['xpln2']['evals'] += evals2
                result_table['top']['evals'] += len(data.rows)  # betters() evaluates on each row

                for i in range(len(comparisons)):
                    (base, diff), result = comparisons[i]

                    if result is None:
                        comparisons[i][1] = ["=" for _ in range(len(data.cols.y))]  # initialize with '='

                    for k in range(len(data.cols.y)):
                        if comparisons[i][1][k] == "=":
                            base_y = result_table[base]["data"][count].cols.y[k]
                            diff_y = result_table[diff]["data"][count].cols.y[k]
                            equals = bootstrap(base_y.vals(), diff_y.vals()) and \
                                     cliffs_delta(base_y.vals(), diff_y.vals())

                            if not equals:
                                if base == diff:  # when comparing same algo on same data should never fail
                                    print(f"WARNING: {base} to {diff} comparison failed for {k}")
                                    print(f"""Preview: {result_table[base]["data"][count].cols.y[k].txt}""")

                                comparisons[i][1][k] = "≠"
                count += 1

        # generate the stats table
        headers = [y.txt for y in data.cols.y]
        data_table = []

        result_table['sway1 (with zitzler domination)'] = result_table.pop('sway1')
        result_table['sway2 (with boolean domination)'] = result_table.pop('sway2')


        for k, v in result_table.items():
            stats = get_stats(v["data"])
            stats_list = [k] + [stats[y] for y in headers]
            stats_list += [v['evals'] / options['niter']]
            data_table.append(stats_list)

        print(tabulate(data_table, headers=headers + ["n_evals avg"], numalign="right"))
        print()

        comparison_table = []
        for [base, diff], result in comparisons:
            comparison_table.append([f"{base} to {diff}"] + result)
        print(tabulate(comparison_table, headers=headers, numalign="right"))

    sys.exit(fails)


if __name__ == "__main__":
    main()
