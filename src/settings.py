THE = {}

HELP = """
USAGE: python main.py [OPTIONS] [-g ACTIONS]

OPTIONS:
  -b  --bins            initial number of bins              = 16
  -c  --cliff           cliff's delta threshold             = .147
  -co --cohen           cohen value                         = .35
  -d  --d               different is over sd*d              = .35
  -f  --file            data file                           = ../etc/data/auto93.py
  -F  --Far             distance to distant                 = .95
  -g  --go              start-up action                     = nothing
  -h  --help            show help                           = false
  -H  --Halves          search space for clustering         = 512
  -m  --min             size of smallest cluster            = .5
  -M  --Max             numbers                             = 512
  -n  --niter           number of iterations to run         = 20
  -o  --conf            conf value                          = 0.05
  -p  --p               dist coefficient                    = 2
  -r  --rest            how many of rest to sample          = 4
  -R  --Reuse           child splits reuse a parent pole    = true
  -s  --seed            random number seed                  = 937162211
  -S  --SigLevel        significance level                  = 5
  -w  --width           width                               = 40
  -x  --bootstrap       number of samples to bootstrap      = 512
  -hs --hpoSamplesSize  hbo study sample size               = 50
"""

EXAMPLE_FUNCS = {}

SEED = 937162211

RESULT_TABLE = {'all': [], 'sway1': [], 'sway2': [], 'sway3': [], 'xpln1': [], 'xpln2': [], 'xpln3': [], 'top': []}

COMPARISONS = [[['all', 'all'], None],
               [['all', 'sway1'], None],
               [['all', 'sway2'], None],
               [['sway1', 'sway2'], None],
               [['sway1', 'xpln1'], None],
               [['sway2', 'xpln2'], None],
               [['sway3', 'xpln3'], None],
               [['sway1', 'top'], None],
               [['xpln1', 'top'], None]]