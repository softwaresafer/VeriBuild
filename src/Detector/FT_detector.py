import io
import sys
import os
import json
import time
import networkx as nx
from Util.parser import *
from Util.operation import *


def is_FileTarConsistent(outputfilename, target, target2dir_map):
    curdir = target2dir_map[target]
    expectedfilename = os.path.normpath(curdir + "/" + target)
    if (expectedfilename == outputfilename):
        return True, target
    if (not outputfilename.startswith(curdir)):
        return False, outputfilename
    tmpname = outputfilename[len(curdir):].lstrip("/")
    # print("-----------")
    # print(target)
    # print(outputfilename)
    # print(curdir)
    # print(tmpname)
    # print("-----------")
    return False, tmpname


# File-Target-Inconsistency
def FT_detect(G, CDG, DDG, target2dir_map, fileIndexMap, outputpath):
    time_start = time.time()
    pseudotarget_list = get_pseudotarget(DDG)
    IO_compare_graph = {}
    filterdirs = get_filterfiles()
    target_resultfile_map = {}
    isFT = True
    resultnum = 0

    for target in DDG.keys():
        target_output_set = set(DDG[target]["output"].keys())
        target_output_set = set(filter(lambda filename: file_filter(filename, filterdirs), target_output_set))
        split_subtargets = []
        if (not target in CDG.keys()):
            continue
        if (target in fileIndexMap.keys()):
            continue
        succtarlist = G.predecessors(target)
        if (succtarlist == []):
            continue
        for succtarget in succtarlist:
            succtarget_input_set = set(DDG[succtarget]["input"].keys())
            useable_output_set = succtarget_input_set & target_output_set
            tmp_split_subtargets = []
            if (useable_output_set == set([])):
                continue
            for useable_outputfile in useable_output_set:
                isConsistentFT, subtarget = is_FileTarConsistent(useable_outputfile, target, target2dir_map)
                if (isConsistentFT):
                    tmp_split_subtargets = []
                    split_subtargets = []
                    isFT = False
                    break
                else:
                    tmp_split_subtargets.append(subtarget)
            if (not isFT):
                break
            split_subtargets.extend(tmp_split_subtargets)
      
        IO_compare_graph[target] = {}
        IO_compare_graph[target]["File-Target Inconsistency"] = split_subtargets
        if (len(IO_compare_graph[target]["File-Target Inconsistency"]) == 0):
            continue
        resultnum += 1
        print(target)
        print(split_subtargets)
        print(target2dir_map[target])
        print(succtarlist)
        resultfile = open(outputpath + "/FT_" + str(resultnum) + ".json", "w")
        json.dump(IO_compare_graph[target], resultfile, indent=4)
        target_resultfile_map[target] = resultnum
        
    time_end = time.time()
    f = open(outputpath + '/FT.json', 'w')
    json.dump(IO_compare_graph, f, indent=4)
    print("FT number:")
    print(resultnum)
    return (time_end - time_start), target_resultfile_map, IO_compare_graph