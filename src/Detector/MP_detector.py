import io
import sys
import os
import json
import time
from Util.parser import *
from Util.operation import *

def MP_detect(CDG, DDG, restb, fileIndexMap, outputpath):
    time_start = time.time()
    pseudotarget_list = get_pseudotarget(DDG)
    IO_compare_graph = {}
    filterdirs = get_filterfiles()
    target_resultfile_map = {}
    resultnum = 0

    for target in DDG.keys():
        if (not target in CDG.keys()):
            continue
        if (target in fileIndexMap.keys() or target in pseudotarget_list):
            IO_compare_graph[target] = {}
            IO_compare_graph[target]["Missing Prerequisites"] = []
            target_resultfile_map[target] = None
        else:
            inputset = set(DDG[target]["input"])
            for outputfile in DDG[target]["output"].keys():
                if (outputfile in inputset):
                    if (DDG[target]["input"][outputfile] > DDG[target]["output"][outputfile]):
                        inputset.remove(outputfile)
            preoutput = {}
            for prerequisite in CDG[target]:
                if (not prerequisite in restb.keys()):
                    continue
                preoutput.update(restb[prerequisite])
            IO_compare_graph[target] = {}
            IO_compare_graph[target]["Missing Prerequisites"] = list(inputset.difference(set(preoutput.keys())))
            IO_compare_graph[target]["Missing Prerequisites"] = list(filter(lambda filename: file_filter(filename, filterdirs), IO_compare_graph[target]["Missing Prerequisites"]))
        
        if (len(IO_compare_graph[target]["Missing Prerequisites"]) == 0):
            continue
        resultnum += 1
        # print("success")
        resultfile = open(outputpath + "/MP_" + str(resultnum) + ".json", "w")
        json.dump(IO_compare_graph[target], resultfile, indent=4)
        target_resultfile_map[target] = resultnum
    time_end = time.time()
    file5 = open(outputpath + '/MP.json', 'w')
    json.dump(IO_compare_graph, file5, indent=4)
    return (time_end - time_start), target_resultfile_map, IO_compare_graph
