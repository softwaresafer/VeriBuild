import io
import sys
import os
import json
import time
from Util.parser import *
from Util.operation import *

def FR_detect(G, CDG, DDG, fileIndexMap, outputpath):
    time_start = time.time()
    IO_compare_graph = {}
    IO_compare_graph["OO"] = []
    IO_compare_graph["IO"] = []
    filterdirs = get_filterfiles()
    toptargets = list(filter(lambda node: G.in_degree(node) == 0, list(G.nodes())))

    print("begin")
    relationMatrix = get_childRelationMatrixClosure(CDG)
    resultnum = 0

    file7 = open(outputpath + '/relation.json', 'w')
    json.dump(relationMatrix, file7, indent=4)
    print("relation matrix over")

    toptargets_table = {}
    count = 0

    noleaf = []
    for target in CDG.keys():
        if (CDG[target] == [] or (not target in DDG.keys())):
            continue
        else:
            noleaf.append(target)

    for target in CDG.keys():
        toptargets_table[target] = set([])
        print(count)
        print(len(set(CDG.keys())))
        print(target)
        count += 1
        for toptarget in toptargets:
            if (toptarget == ""):
                continue
            if (relationMatrix[toptarget][target] or relationMatrix[target][toptarget]):
                toptargets_table[target].add(toptarget)

    print("toptargets over")

    for target1 in noleaf:
        print(target1)
        for target2 in noleaf:
            if (target2 == target1 or target1 == "" or target2 == ""):
                continue
            if (relationMatrix[target1][target2] or relationMatrix[target2][target1]):
                continue
            if ((toptargets_table[target1] & toptargets_table[target2]) == set([])):
                continue
            inputset1 = set(DDG[target1]["input"].keys())
            outputset1 = set(DDG[target1]["output"].keys())
            inputset2 = set(DDG[target2]["input"].keys())
            outputset2 = set(DDG[target2]["output"].keys())
            if (outputset1 & outputset2 != set([]) and (not [target2, target1] in IO_compare_graph["OO"])):
                IO_compare_graph["OO"].append([target1, target2])
                resultnum += 1
            if (inputset1 & outputset2 != set([])):
                IO_compare_graph["IO"].append([target1, target2])
                resultnum += 1

    time_end = time.time()
    file7 = open(outputpath + '/FR.json', 'w')
    json.dump(IO_compare_graph, file7, indent=4)
    print("FR number:")
    print(resultnum)
    return (time_end - time_start), IO_compare_graph