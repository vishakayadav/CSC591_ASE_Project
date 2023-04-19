# Take features out and see what happens
# Might need to take out multiple since nothing really happened with the regular csv
import csv

from scikittests import *
import os

from src.utils import the


def removeFeatures(remFeature):
    nrows = []
    diffs = []
    with open("../../" + the["file"], "r") as f:
        r = csv.reader(f)
        start = True
        pvals = []
        for row in r:
            if start:
                for i in range(len(row)):
                    item = row[i].rstrip()
                    if item[-1] == "X" or i == remFeature:
                        pvals.append(i)
                start = False
                pvals.reverse()
            else:
                for i in range(len(row)):
                    item = row[i].rstrip()
                    # Not sure if this works
                    try:
                        if item != "?":
                            float(item)
                    except:
                        if not item in diffs:
                            diffs.append(item)
                        row[i] = str(diffs.index(item))
            row[-1] = row[-1].rstrip()
            for val in pvals:
                row.pop(val)
            nrows.append(row)

    with open(config.currFile, "w", newline='') as f:
        w = csv.writer(f)
        w.writerows(nrows)


def ablationRunner():
    fData = DATA(config.the["file"])
    if not os.path.exists("./ablation/"):
        os.mkdir("./ablation/")
    os.chdir("./ablation/")
    for col in range(len(fData["cols"]["names"])):
        colName = fData["cols"]["names"][col].rstrip()
        if colName[-1] == "-" or colName[-1] == "+":
            continue
        if not os.path.exists("./" + str(col) + "/"):
            os.mkdir(str(col))
        os.chdir("./" + str(col) + "/")
        removeFeatures(col)
        data = DATA("curr.csv")
        val = np.genfromtxt(fname=config.currFile, delimiter=",", dtype=float, skip_header=1, missing_values="?",
                            filling_values=0)

        bestCluster = {}
        bestClusterEvals = {}
        bestExplain = {}
        bestExplainValues = {}
        bestExplainScores = {}

        regularClusters = {}
        regularExplains = {}

        for i in range(20):
            print("Current run: %d" % i)
            top, groups, bestVal, evals, regular = BisectClusterer(data, val)
            regularClusters[len(regularClusters)] = regular
            bestClusterEvals[len(bestClusterEvals)] = evals
            # res = betters(top, 1)
            # bestCluster[len(bestCluster)] = res[0][0]
            bestCluster[len(bestCluster)] = stats(top)[0]
            features, bestExplains, score = RFExplainer(data, val, groups, bestVal)
            bestExplainScores[len(bestExplainScores)] = score
            regularExplains[len(regularExplains)] = bestExplains
            top = DATA(data, bestExplains)
            # res = betters(top, 1)
            # bestExplainValues[len(bestCluster)] = res[0][0]
            bestExplainValues[len(bestExplainValues)] = stats(top)[0]
            for ind in range(len(features)):
                feat = features[ind]
                if feat in bestExplain.keys():
                    bestExplain[feat] += (len(features) - ind)
                else:
                    bestExplain[feat] = len(features) - ind

        bestExplainList = []
        for k, v in bestExplain.items():
            bestExplainList.append([k, v])

        def sf(i):
            return -i[1]

        bestExplainList.sort(key=sf)

        topTenBest = {}
        for i in range(10):
            try:
                item = bestExplainList[i]
                name = item[0].rstrip()
                if not (name[-1] == "-" or name[-1] == "+"):
                    topTenBest[len(topTenBest)] = name
            except IndexError:
                break

        bestClusterData = getAvg(bestCluster)
        avgEval = getAvg(bestClusterEvals)["Evals"]
        print("Average of the median values for the cluster with %5s evals over 20 runs" % avgEval, bestClusterData)

        bestExplainData = getAvg(bestExplainValues)
        avgScore = getAvg(bestExplainScores)["Score"]
        print("Average of the median values for the explainer with %5s validation score over 20 runs" % avgScore,
              bestExplainData)

        # avg = 0
        # for k, num in bestClusterEvals.items():
        #   avg += num
        # avg /= len(bestClusterEvals)
        avg_eval = {avgEval}
        avg_score = {avgScore}

        print("Best features extracted:")
        for i in range(len(topTenBest)):
            print("%d. %s" % (i + 1, topTenBest[i]))

        with open("clusterRes.txt", "wb") as f:
            pickle.dump(bestClusterData, f)

        with open("clusterEvalRes.txt", "wb") as f:
            pickle.dump(avg_eval, f)

        with open("explainResults.txt", "wb") as f:
            pickle.dump(topTenBest, f)

        with open("explainValuesResults.txt", "wb") as f:
            pickle.dump(bestExplainData, f)

        with open("explainScoreAvg.txt", "wb") as f:
            pickle.dump(avg_score, f)

        with open("regularCluster.txt", "wb") as f:
            pickle.dump(regularClusters, f)

        with open("regularExplain.txt", "wb") as f:
            pickle.dump(regularExplains, f)

        os.chdir("../")