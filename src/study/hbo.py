import itertools
import math
import random
from copy import deepcopy
from typing import List

import numpy as np

from src.contrast_set import xpln, selects
from src.data import DATA
from hyperopt import hp, fmin, tpe, Trials, STATUS_OK

from src.utils import the


class HBO():
    def __init__(self):
        self.the = deepcopy(the)
        self.data = DATA(self.the["file"])
        self.params_grid = {
            "bins": [round(i, 2) for i in list(np.arange(2, 15, 1))],
            "Far": [round(i, 2) for i in list(np.arange(0.5, 1, 0.05))],
            "min": [round(i, 2) for i in list(np.arange(0.5, 1, 0.05))],
            "Max": [round(i, 2) for i in list(np.arange(12, 2500, 500))],
            "Halves": [round(i, 2) for i in list(np.arange(12, 3000, 500))],
            "conf": [round(i, 2) for i in list(np.arange(0.5, 1, 0.05))],
            "p": [round(i, 2) for i in list(np.arange(0.5, 10, 0.5))],
            "rest": [round(i, 2) for i in list(np.arange(1, 10, 1))]
        }

    def _better_dicts(self, dict1, dict2, data):
        s1, s2, x, y = 0, 0, None, None

        for col in data.cols.y:
            x = col.norm(dict1.get(col.txt))
            y = col.norm(dict2.get(col.txt))
            s1 -= math.exp(col.w * (x - y) / len(data.cols.y))
            s2 -= math.exp(col.w * (y - x) / len(data.cols.y))

        return s1 / len(data.cols.y) < s2 / len(data.cols.y)

    def _generate_hpo_params_combo(self) -> List[dict]:
        """
        Returns the hyperparameter combinations to be evaluated.
        """
        combos = list(itertools.product(*self.params_grid.values()))
        all_params_combos = [dict(zip(self.params_grid.keys(), params)) for params in combos]
        return all_params_combos

    def _compute_sway_and_xpln(self) -> ("DATA", "DATA", int):
        best, rest, evals = self.data.sway()
        rule, _ = xpln(self.data, best, rest)
        xpln_data = None
        if rule:
            xpln_data = DATA(self.data, selects(rule, self.data.rows))
        return best, xpln_data, evals

    def hbo_minimal_sampling(self):
        optimial_sway_hyper_params = []
        least_sway_evals = -1
        least_xpln_evals = -1
        best_sway = ""
        best_xpln = ""
        best_top = ""

        hp_combos_sample = random.sample(self._generate_hpo_params_combo(), self.the['hpoSamplesSize'])

        for hp_param in hp_combos_sample:
            for k, v in hp_param.items():
                self.the[k] = v
            best, xpln_data, evals = self._compute_sway_and_xpln()
            top, _ = self.data.betters(len(best.rows))
            top = self.data.clone(top)

            if xpln_data:
                if best_xpln == "":
                    best_sway = best.stats('mid', best.cols.y, 2)
                    best_xpln = xpln_data.stats('mid', xpln_data.cols.y, 2)
                    best_top = top.stats('mid', top.cols.y, 2)
                    optimial_sway_hyper_params = hp_param
                    least_sway_evals = evals
                    least_xpln_evals = evals
                else:
                    current_sway = best.stats('mid', best.cols.y, 2)
                    if self._better_dicts(current_sway, best_sway, self.data):
                        best_sway = current_sway
                        optimial_sway_hyper_params = hp_param
                        least_sway_evals = evals
        the.update(optimial_sway_hyper_params)
        print('\033[92m HPO Minimal Sampling Results \033[0m')
        print('\033[1m Best Params: \033[0m', optimial_sway_hyper_params)
        print("\033[1m Stats on Best Params: \033[0m")
        print("\t all: \t\t", self.data.stats('mid', self.data.cols.y, 2))
        print("\t sway:", least_sway_evals, "evals", best_sway)
        print("\t xpln:", least_xpln_evals, "evals", best_xpln)
        print("\t top", len(self.data.rows), "evals", best_top)
        print("\n\n")

    def _hyperopt_obj(self, params):
        current_sway = {}
        current_xpln = {}
        best_top = {}
        sum = 0
        for k, v in params.items():
            self.the[k] = v
        best, xpln_data, evals = self._compute_sway_and_xpln()
        top, _ = self.data.betters(len(best.rows))
        top = self.data.clone(top)

        if xpln_data:
            current_sway = best.stats('mid', best.cols.y, 2)
            current_xpln = xpln_data.stats('mid', xpln_data.cols.y, 2)
            best_top = top.stats('mid', top.cols.y, 2)

            for col in self.data.cols.y:
                x = current_sway.get(col.txt)
                sum += x * col.w
        return {"loss": sum, "status": STATUS_OK, "evals": evals, "sway": current_sway,
                "xpln": current_xpln, "top": best_top, "params": params}

    def hpo_hyperopt_params(self):
        space = {}
        trials = Trials()
        for key in self.params_grid.keys():
            space[key] = hp.choice(key, self.params_grid[key])

        fmin(self._hyperopt_obj, space, algo=tpe.suggest, max_evals=self.the['hpoSamplesSize'], trials=trials)
        trial_loss = np.asarray(trials.losses(), dtype=float)
        best_ind = np.argmin(trial_loss)
        best_trial = trials.trials[best_ind]
        # print("\033[92m HPO Hyperopt \033[0m")
        print("\033[1m HPO Hyperopt Best Params: \033[0m", best_trial['result']['params'], "\n\n")
        # print("\033[1m Stats on Best Params: \033[0m")
        # print("\t all: \t\t", self.data.stats('mid', self.data.cols.y, 2))
        # print("\t sway:", best_trial['result']['evals'], "evals", best_trial['result']['sway'])
        # print("\t xpln:", best_trial['result']['evals'], "evals", best_trial['result']['xpln'])
        # print("\t top:", len(self.data.rows), "evals", best_trial['result']['top'])
        # print()
        return best_trial['result']['params'], best_trial['result']['evals']
