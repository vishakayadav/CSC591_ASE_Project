THE = {}

HELP = """
USAGE: python main.py [OPTIONS] [-g ACTIONS]

OPTIONS:
  -b  --bins        initial number of bins              = 16
  -c  --cliff       cliff's delta threshold             = .147
  -d  --d           different is over sd*d              = .35
  -f  --file        data file                           = ../etc/data/auto93.csv
  -F  --Far         distance to distant                 = .95
  -g  --go          start-up action                     = nothing
  -h  --help        show help                           = false
  -H  --Halves      search space for clustering         = 512
  -m  --min         size of smallest cluster            = .5
  -M  --Max         numbers                             = 512
  -n  --niter       number of iterations to run         = 20
  -o  --conf        conf value                          = 0.05
  -p  --p           dist coefficient                    = 2
  -r  --rest        how many of rest to sample          = 4
  -R  --Reuse       child splits reuse a parent pole    = true
  -s  --seed        random number seed                  = 937162211
  -x  --bootstrap   number of samples to bootstrap      = 512
"""

EXAMPLE_FUNCS = {}

SEED = 937162211

RESULT_TABLE = {'all': {'evals': 0, 'data': []},
                'sway1': {'evals': 0, 'data': []},
                'sway2': {'evals': 0, 'data': []},
                'xpln1': {'evals': 0, 'data': []},
                'xpln2': {'evals': 0, 'data': []},
                'top': {'evals': 0, 'data': []}}

COMPARISONS = [[['all', 'all'], None],
               [['all', 'sway1'], None],
               [['all', 'sway2'], None],
               [['sway1', 'sway2'], None],
               [['sway1', 'xpln1'], None],
               [['sway2', 'xpln2'], None],
               [['sway1', 'top'], None],
               [['xpln1', 'top'], None]]