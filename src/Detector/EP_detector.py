import io
import sys
import os
import json
import time
from Util.parser import *
from Util.operation import *


def EP_detect(CDG, DDG, restb, fileIndexMap, outputpath):
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
            IO_compare_graph[target]["Excessive Prerequisites"] = []
            target_resultfile_map[target] = None
        else:
            IO_compare_graph[target] = {}
            IO_compare_graph[target]["Excessive Prerequisites"] = []
            # Input set are those files that we really care about.
            inputset = set(DDG[target]["input"].keys())

            # Input file set should not be filtered.
            # inputset = set(filter(lambda filename: file_filter(filename, filterdirs), list(inputset)))  
            
            prerequisite_list = CDG[target]

            # Dict from inputfile-> No of appearence times 
            input_file_dict = {input_file:0 for input_file in inputset}
            for pre in prerequisite_list:
                if (not pre in restb.keys()):
                    continue
                for resfile in restb[pre]:
                    if resfile in input_file_dict.keys():
                        input_file_dict[resfile] = input_file_dict[resfile]+1

            # For each prerequiste P, we test whether the input set changes if P is removed. 
            for pre in prerequisite_list:
                if (not pre in restb.keys()):
                    continue

                is_essential_target = False
                for resfile in restb[pre]:
                    if resfile in input_file_dict.keys():
                        if input_file_dict[resfile] == 1:
                            # This target pre is the only provider of the resfile.  
                            # We mark it as an essential target. 
                            is_essential_target = True
                            # breaking for performance considerations. 
                            break  

                if not is_essential_target:
                    # Report it
                    print("Excessive Detected : {} -> {}".format(target, pre))      
                    IO_compare_graph[target]["Excessive Prerequisites"].append(pre)

            # originaloutputset = set([])
            # cacheset = set([])
            # for pre in prerequisite_list:
            #     if (not pre in restb.keys()):
            #         continue
            #     for resfile in restb[pre]:
            #         if (resfile in originaloutputset):
            #             cacheset.add(resfile)
            #         else:
            #             originaloutputset.add(resfile)

            # print("\t Target %s Cache Set %s  OriginalSet %s" % (target, cacheset, originaloutputset))

            # # Only check EP for immediate prerequisites
            # for pre in prerequisite_list:
            #     # Check EP condition
            #     if (not pre in restb.keys()):
            #         print("\t %s is not in the restb" % (pre))
            #         continue
            #     if (set(restb[pre]) - cacheset == set([])):
            #         IO_compare_graph[target]["Excessive Prerequisites"].append(pre)
            #         print("Excessive Detected : %s -> %s" % {target, pre})
        IO_compare_graph[target]["Excessive Prerequisites"] = list(filter(lambda filename: file_filter(filename, filterdirs), IO_compare_graph[target]["Excessive Prerequisites"]))
        if (len(IO_compare_graph[target]["Excessive Prerequisites"]) == 0):
            continue
        resultnum += 1
        # print("success")
        resultfile = open(outputpath + "/EP_" + str(resultnum) + ".json", "w")
        json.dump(IO_compare_graph[target], resultfile, indent=4)
        target_resultfile_map[target] = resultnum

    time_end = time.time()
    file6 = open(outputpath + '/EP.json', 'w')
    json.dump(IO_compare_graph, file6, indent=4)
    return (time_end - time_start), target_resultfile_map, IO_compare_graph
