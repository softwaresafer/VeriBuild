import io
import sys
import os
import json
import time

def is_equal_target(target, item):
    return target == item             # TODO


def is_approximately_contains(target, target_map):
    item_matched = None
    for item in target_map.keys():
        if is_equal_target(target, item):
            item_matched = item
    return item_matched


def is_approximately_in(target, target_set):
    item_matched = None
    for item in target_set:
        if is_equal_target(target, item):
            item_matched = item
    return item_matched


def compare_report(mkcheck_edge, mkcheck_map, vemake_edge, vemake_map):
    mkcheck_own = []
    vemake_own = []
    shared_report = []

    for edge in mkcheck_edge:
        [target, pre] = edge
        # if (not target in vemake_map.keys()):
        target_item = is_approximately_contains(target, vemake_map)
        if target_item is None:
            mkcheck_own.append(edge)
            continue
        # if (not pre in vemake_map[target]):
        target_set = is_approximately_in(target, vemake_map[target_item])
        if not is_approximately_in(pre, target_set):
            mkcheck_own.append(edge)
            continue
        shared_report.append(edge)

    print("debug--------------------------------")
    print(len(vemake_edge))

    for edge in vemake_edge:
        [target, pre] = edge
        # if (not target in mkcheck_map.keys()):
        target_item = is_approximately_contains(target, mkcheck_map)
        if target_item is None:
            vemake_own.append(edge)
            continue
        # if (not pre in mkcheck_map[target]):
        target_set = is_approximately_in(target, mkcheck_map[target_item])
        if not is_approximately_in(pre, target_set):
            vemake_own.append(edge)
            continue

    return mkcheck_own, vemake_own, shared_report


def collect_mkcheck_report(projectname):
    basedir = "/home/nand/Vemake/buildfuzz_results/"
    fuzz_resultfile = open(basedir + "mkcheck_fuzz_stdout_" + projectname + ".txt")
    race_resultfile = open(basedir + "mkcheck_race_stdout_" + projectname + ".txt")
    MP_edge = []
    EP_edge = []

    target = ""
    prerequisite = ""
    while True:
        line = fuzz_resultfile.readline()
        if not line:
            break
        if (line.startswith("[")):
            index1 = line.find("]")
            index2 = line.find(":")
            prerequisite = line[(index1 + 1): index2].replace(" ","").replace("\n","")
        elif (line.lstrip(" ").startswith("-")):
            index1 = line.find("-")
            index2 = line.rfind("(")
            target = line[(index1 + 1):index2].replace(" ", "")
            index  = target.find(projectname + "/")
            target = target[(index + len(projectname)):].lstrip("/").replace("\n","")
            index = prerequisite.find(projectname + "/")
            prerequisite_new = prerequisite[(index + len(projectname)):].lstrip("/").replace("\n","")
            MP_edge.append([target, prerequisite_new])
        elif (line.lstrip(" ").startswith("+")):
            index1 = line.find("+")
            index2 = line.rfind("(")
            target = line[(index1 + 1):index2].replace(" ", "")
            index  = target.find(projectname + "/")
            target = target[(index + len(projectname)):].lstrip("/").replace("\n","")
            index = prerequisite.find(projectname + "/")
            prerequisite_new = prerequisite[(index + len(projectname)):].lstrip("/").replace("\n","")
            EP_edge.append([target, prerequisite_new])

    isRCReportBegin = False
    while True:
        line = race_resultfile.readline()
        if not line:
            break
        if (line.startswith("Missing edges:")):
            isRCReportBegin = True
            continue
        if (not isRCReportBegin):
            continue
        index = line.find("->")
        if (index == -1):
            continue
        else:
            target = line[(index + 2):].replace(" ", "").replace("\n","")
            prerequisite = line[:index].replace(" ", "").replace("\n","")
            index  = target.find(projectname + "/")
            target = target[(index + len(projectname)):].lstrip("/").replace("\n","")
            index = prerequisite.find(projectname + "/")
            prerequisite_new = prerequisite[(index + len(projectname)):].lstrip("/").replace("\n","")
            MP_edge.append([target, prerequisite_new])

    # print(MP_edge)
    # print(EP_edge)
    return MP_edge, EP_edge

        
def collect_vemake_report(projectname):   # TODO: error prone, copied from collect_mkcheck_report
    # Load MP and EP
    basedir = "/home/vemakecreator/CODEBASE/veribuild/Vemake/testbase/testoutput/"
    MP_file = open(basedir + projectname + '/MP.json', 'r+')
    MP_result = eval(MP_file.read())

    print("--------------------------------------------")
    print("DEBUG: MP_file")
    print(MP_result)
    print("--------------------------------------------")

    EP_file = open(basedir + projectname + '/EP.json', 'r+')
    EP_result = eval(EP_file.read())

    print("--------------------------------------------")
    print("DEBUG: EP_file")
    print(EP_result)
    print("--------------------------------------------")

    shortDDG_file = open(basedir + projectname + '/shortDDG.json', 'r+')
    shortDDG = eval(shortDDG_file.read())

    print("--------------------------------------------")
    print("DEBUG: shortDDG")
    print(shortDDG)
    print("--------------------------------------------")

    MP_edge = []
    EP_edge = []
    
    for target in MP_result.keys():
        if (not target in shortDDG.keys()):
            continue
        mplist = MP_result[target]["Missing Prerequisites"]
        tarlist = shortDDG[target]["output"].keys()
        print("target_list")
        print(tarlist)
        for pre in mplist:
            for taritem in tarlist:
                index  = taritem.find(projectname + "/")
                if (index != -1):
                    taritem = taritem[(index + len(projectname)):].lstrip("/")    
                index = pre.find(projectname + "/")
                if (index != -1):
                    pre = pre[(index + len(projectname)):].lstrip("/")
                # MP_edge.append(["src/" + taritem, pre])
                MP_edge.append([taritem, pre])

    for target in EP_result.keys():
        if (not target in shortDDG.keys()):
            continue
        eptarget_list = EP_result[target]["Excessive Prerequisites"]
        tarlist = shortDDG[target]["output"].keys()
        for taritem in tarlist:
            for pre in eptarget_list:
                if (not pre in shortDDG.keys()):
                    continue
                eplist = shortDDG[pre]["output"].keys()
                for epfile in eplist:
                    index  = taritem.find(projectname + "/")
                    target_new = taritem
                    if (index != -1):
                        target_new = taritem[(index + len(projectname)):].lstrip("/")
                    index = epfile.find(projectname + "/")
                    if (index != -1):
                        epfile = epfile[(index + len(projectname)):].lstrip("/")
                    # EP_edge.append(["src/" + target_new, epfile])
                    EP_edge.append([target_new, epfile])
    
    # print(MP_edge)
    # print(EP_edge)
    print("--------------------------------------------")
    print("DEBUG: MP")
    print(len(MP_edge))
    print("--------------------------------------------")
    print(" ")
    print("--------------------------------------------")
    print("DEBUG: EP")
    print(len(EP_edge))
    print("--------------------------------------------")

    return MP_edge, EP_edge


def collect_vemake_report_backup(projectname):  # TODO: error prone, copied from collect_mkcheck_report
    # Load MP and EP
    basedir = "/home/vemakecreator/CODEBASE/veribuild/Vemake/testbase/testoutput/"
    MP_file = open(basedir + projectname + '/MP.json', 'r+')
    MP_result = eval(MP_file.read())

    print("--------------------------------------------")
    print("DEBUG: MP_file")
    print(MP_result)
    print("--------------------------------------------")

    EP_file = open(basedir + projectname + '/EP.json', 'r+')
    EP_result = eval(EP_file.read())

    print("--------------------------------------------")
    print("DEBUG: EP_file")
    print(EP_result)
    print("--------------------------------------------")

    shortDDG_file = open(basedir + projectname + '/shortDDG.json', 'r+')
    shortDDG = eval(shortDDG_file.read())

    MP_edge = []
    EP_edge = []

    for target in MP_result.keys():
        mplist = MP_result[target]["Missing Prerequisites"]
        if (not target in shortDDG.keys()):
            continue
        tarlist = shortDDG[target]["output"].keys()
        for pre in mplist:
            for taritem in tarlist:
                index = taritem.find(projectname + "/")
                if (index != -1):
                    taritem = taritem[(index + len(projectname)):].lstrip("/")
                index = pre.find(projectname + "/")
                if (index != -1):
                    pre = pre[(index + len(projectname)):].lstrip("/")
                # MP_edge.append(["src/" + taritem, pre])
                MP_edge.append([taritem, pre])

    for target in EP_result.keys():
        eptarget_list = EP_result[target]["Excessive Prerequisites"]
        if (not target in shortDDG.keys()):
            continue
        tarlist = shortDDG[target]["output"].keys()
        for taritem in tarlist:
            for pre in eptarget_list:
                if (not pre in shortDDG.keys()):
                    continue
                eplist = shortDDG[pre]["output"].keys()
                for epfile in eplist:
                    index = taritem.find(projectname + "/")
                    target_new = taritem
                    if (index != -1):
                        target_new = taritem[(index + len(projectname)):].lstrip("/")
                    index = epfile.find(projectname + "/")
                    if (index != -1):
                        epfile = epfile[(index + len(projectname)):].lstrip("/")
                    # EP_edge.append(["src/" + target_new, epfile])
                    EP_edge.append([target_new, epfile])

    # print(MP_edge)
    # print(EP_edge)
    print("--------------------------------------------")
    print("DEBUG: MP")
    print(len(MP_edge))
    print("--------------------------------------------")
    print(" ")
    print("--------------------------------------------")
    print("DEBUG: EP")
    print(len(EP_edge))
    print("--------------------------------------------")

    return MP_edge, EP_edge


def construct_reportmap(edges):
    reportmap = {}
    for edge in edges:
        [target, pre] = edge
        if (target in reportmap.keys()):
            reportmap[target].add(pre)
        else:
            item = set([])
            item.add(pre)
            reportmap[target] = item
    return reportmap


def compare_run(projectname):
    mkcheck_MP_edge, mkcheck_EP_edge = collect_mkcheck_report(projectname)
    vemake_MP_edge, vemake_EP_edge = collect_vemake_report(projectname)     # Error prone
    mkcheck_MP_map = construct_reportmap(mkcheck_MP_edge)
    mkcheck_EP_map = construct_reportmap(mkcheck_EP_edge)
    vemake_MP_map = construct_reportmap(vemake_MP_edge)
    vemake_EP_map = construct_reportmap(vemake_EP_edge)
    mkcheck_MP_own, vemake_MP_own, shared_MP_report = compare_report(mkcheck_MP_edge, mkcheck_MP_map, vemake_MP_edge, vemake_MP_map)
    mkcheck_EP_own, vemake_EP_own, shared_EP_report = compare_report(mkcheck_EP_edge, mkcheck_EP_map, vemake_EP_edge, vemake_EP_map)

    print("MP: mkcheck own | vemake own | shared")
    print(str(len(mkcheck_MP_own)) + " " + str(len(vemake_MP_own)) + " " + str(len(shared_MP_report)))

    print("EP: mkcheck own | vemake own | shared")
    print(str(len(mkcheck_EP_own)) + " " + str(len(vemake_EP_own)) + " " + str(len(shared_EP_report)))

    # output to compareresultdir
    compare_result = {}
    compare_result["mkcheck_MP_own"] = mkcheck_MP_own
    compare_result["vemake_MP_own"] = vemake_MP_own
    compare_result["shared_MP_report"] = shared_MP_report

    compare_result["mkcheck_EP_own"] = mkcheck_EP_own
    compare_result["vemake_EP_own"] = vemake_EP_own
    compare_result["shared_EP_report"] = shared_EP_report

    compare_result["MP(mkcheck own | vemake own | shared)"] = [len(mkcheck_MP_own), len(vemake_MP_own), len(shared_MP_report)]
    compare_result["EP(mkcheck own | vemake own | shared)"] = [len(mkcheck_EP_own), len(vemake_EP_own), len(shared_EP_report)]
    filex = open("/home/vemakecreator/CODEBASE/veribuild/Vemake/testbase/compare" + projectname + '.json', 'w')
    json.dump(compare_result, filex, indent=4)
    print(compare_report)

    return mkcheck_MP_own, vemake_MP_own, shared_MP_report, mkcheck_EP_own, vemake_EP_own, shared_EP_report


if __name__ == "__main__":
    projectname = sys.argv[1]
    mkcheck_MP_own, vemake_MP_own, shared_MP_report, mkcheck_EP_own, vemake_EP_own, shared_EP_report = compare_run(projectname)