import re
import sys

from src.utils import the, help_string, example_funcs, coerce


def settings(pstr):
    table = {}
    pattern = """\n[\s]+[-][\S]+[\s]+[-][-]([\S]+)[^\n]+= ([\S]+)"""
    r = re.compile(pattern)
    matches = r.findall(pstr)
    for k, v in matches:
        table[k] = coerce(v)
    return table


def cli(options):
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
        for what, fun in example_funcs.items():
            if options["go"] == "all" or what == options["go"]:
                for k, v in saved.items():
                    options[k] = v
                global seed
                seed = options["seed"]
                if example_funcs[what]() == False:
                    fails += 1
                    print("❌ fail:", what)
                else:
                    print("✅ pass:", what)

    sys.exit(fails)


if __name__ == "__main__":
    main()
