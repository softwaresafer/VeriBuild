import io
import sys
import os
import json
import copy
from VeMakeDDG.DDG import *
from parse import *


def CDDG_constructor(CDG, DDG, fileIndexMap):
    CDDG = {}
    for target in CDG.keys():
        inputfiles, outputfiles, createfiles, deletefiles = get_CDDG_item(target, CDG, DDG, fileIndexMap)
        CDDG[target] = {}
        CDDG[target]["input"] = inputfiles
        CDDG[target]["output"] = outputfiles
        CDDG[target]["create"] = createfiles
        CDDG[target]["delete"] = deletefiles
    return CDDG


def merge_deletefiles(deletefiles, subinputfiles, suboutputfiles, subcreatefiles, subdeletefiles, targetIOInfo):
    for subdeletefile in subdeletefiles.keys():
        if (subdeletefile in suboutputfiles.keys()):
            if (suboutputfiles[subdeletefile] > subdeletefiles[subdeletefile]):
                continue
        elif (subdeletefile in deletefiles.keys()):
            if (subdeletefiles[subdeletefile] < deletefiles[subdeletefile]):
                continue
        deletefiles[subdeletefile] = subdeletefiles[subdeletefile]
    deletefiles.update(targetIOInfo["delete"])
    for suboutputfile in targetIOInfo["output"].keys():
        if (suboutputfile in deletefiles.keys()):
            if (targetIOInfo["output"][suboutputfile] > deletefiles[suboutputfile]):
                deletefiles.pop(suboutputfile)
    return deletefiles


def merge_outputfiles(outputfiles, subinputfiles, suboutputfiles, subcreatefiles, subdeletefiles, targetIOInfo):
    for suboutputfile in suboutputfiles.keys():
        if suboutputfile in subdeletefiles.keys():
            if subdeletefiles[suboutputfile] > suboutputfiles[suboutputfile]:
                continue
        elif suboutputfile in outputfiles.keys() and suboutputfiles[suboutputfile] is not None and outputfiles[suboutputfile] is not None:
            if suboutputfiles[suboutputfile] < outputfiles[suboutputfile]:
                continue
        outputfiles[suboutputfile] = suboutputfiles[suboutputfile]
    outputfiles.update(targetIOInfo["output"])
    for subdeletefile in targetIOInfo["delete"].keys():
        if (subdeletefile in outputfiles.keys()):
            if (targetIOInfo["delete"][subdeletefile] > outputfiles[subdeletefile]):
                outputfiles.pop(subdeletefile)
    return outputfiles


def merge_createfiles(createfiles, subinputfiles, suboutputfiles, subcreatefiles, subdeletefiles, targetIOInfo):
    for subcreatefile in subcreatefiles.keys():
        if (subcreatefile in subdeletefiles.keys()):
            if (subdeletefiles[subcreatefile] > subcreatefiles[subcreatefile]):
                continue
        elif (subcreatefile in createfiles.keys()):
            if (subcreatefiles[subcreatefile] < createfiles[subcreatefile]):
                continue
        createfiles[subcreatefile] = subcreatefiles[subcreatefile]
    createfiles.update(targetIOInfo["create"])
    for subdeletefile in targetIOInfo["delete"].keys():
        if (subdeletefile in createfiles.keys()):
            if (targetIOInfo["delete"][subdeletefile] > createfiles[subdeletefile]):
                createfiles.pop(subdeletefile)
    return createfiles


def get_CDDG_item(target, CDG, DDG, fileIndexMap):
    inputfiles = {}
    outputfiles = {}
    createfiles = {}
    deletefiles = {}
    if (CDG[target] == []):
        if (target in fileIndexMap.keys()):
            inputfiles = {fileIndexMap[target]: None}
    elif (target in DDG.keys()):
        prerequisite_list = CDG[target]
        inputfiles.update(DDG[target]["input"])
        for subtarget in prerequisite_list:
            subinputfiles, suboutputfiles, subcreatefiles, subdeletefiles = get_CDDG_item(subtarget, CDG, DDG, fileIndexMap)
            inputfiles.update(subinputfiles)
            outputfiles = merge_outputfiles(outputfiles, subinputfiles, suboutputfiles, subcreatefiles, subdeletefiles, DDG[target])
            createfiles = merge_createfiles(createfiles, subinputfiles, suboutputfiles, subcreatefiles, subdeletefiles, DDG[target])
            deletefiles = merge_deletefiles(deletefiles, subinputfiles, suboutputfiles, subcreatefiles, subdeletefiles, DDG[target])
    return inputfiles, outputfiles, createfiles, deletefiles


def get_DDG_item(target, CDG, DDG, GDDG):
    pseudotarget_list = get_pseudotarget(DDG)
    if (not target in pseudotarget_list):
        if (target in DDG.keys()):
            GDDG[target] = DDG[target]
        return GDDG
    else:
        inputfiles = {}
        outputfiles = {}
        createfiles = {}
        deletefiles = {}
        for subtarget in CDG[target]:
            if (not subtarget in GDDG.keys()):
                GDDG = get_DDG_item(subtarget, CDG, DDG, GDDG)
            if (not subtarget in GDDG.keys()):
                continue
            inputfiles.update(GDDG[subtarget]["input"])
            outputfiles = merge_outputfiles(outputfiles, GDDG[subtarget]["input"], GDDG[subtarget]["output"], GDDG[subtarget]["create"], GDDG[subtarget]["delete"], DDG[target])
            createfiles = merge_createfiles(createfiles, GDDG[subtarget]["input"], GDDG[subtarget]["output"], GDDG[subtarget]["create"], GDDG[subtarget]["delete"], DDG[target])
            deletefiles = merge_deletefiles(deletefiles, GDDG[subtarget]["input"], GDDG[subtarget]["output"], GDDG[subtarget]["create"], GDDG[subtarget]["delete"], DDG[target])
        GDDG[target] = {}
        GDDG[target]["input"] = inputfiles
        GDDG[target]["output"] = outputfiles
        GDDG[target]["create"] = createfiles
        GDDG[target]["delete"] = deletefiles
        return GDDG


def get_GDDG(CDG, DDG):
    GDDG = {}
    for target in CDG.keys():
        if (not target in GDDG.keys()):
            GDDG = get_DDG_item(target, CDG, DDG, GDDG)
    return GDDG


def get_resource(CDG, DDG, GDDG, fileIndexMap, target, restb):
    resource_list = {}
    if (target in restb.keys()):
        return restb
    if (not target in CDG.keys()):
        return restb
    if (CDG[target] == []):
        restb[target] = DDG[target]["output"]
        return restb
    else:
        for subtarget in CDG[target]:
            restb = get_resource(CDG, DDG, GDDG, fileIndexMap, subtarget, restb)
            if (not subtarget in restb.keys()):
                continue
            resource_list.update(restb[subtarget])
        resource_list.update(DDG[target]["output"])
        for deletefile in GDDG[target]["delete"].keys():
            if (deletefile in resource_list.keys()):
                if (GDDG[target]["delete"][deletefile] > resource_list[deletefile]):
                    resource_list.pop(deletefile)
        for staticFile in fileIndexMap.keys():
            if (fileIndexMap[staticFile] in resource_list.keys()):
                resource_list.pop(fileIndexMap[staticFile])
        restb[target] = resource_list
        return restb

def get_resource_ninja(CDG, DDG, GDDG, fileIndexMap, target, restb):
    resource_list = {}
    if (target in restb.keys()):
        return restb
    if (CDG[target] == []):
        restb[target] = DDG[target]["output"]
        return restb
    else:
        for subtarget in CDG[target]:
            restb = get_resource_ninja(CDG, DDG, GDDG, fileIndexMap, subtarget, restb)
            resource_list.update(restb[subtarget])
        resource_list.update(DDG[target]["output"])
        for deletefile in GDDG[target]["delete"].keys():
            if (deletefile in resource_list.keys()):
                if (GDDG[target]["delete"][deletefile] > resource_list[deletefile]):
                    resource_list.pop(deletefile)
        # for staticFile in fileIndexMap.keys():
        #     if (fileIndexMap[staticFile] in resource_list.keys()):
        #         resource_list.pop(fileIndexMap[staticFile])
        restb[target] = resource_list
        return restb


def get_resourceTable(CDG, DDG, GDDG, fileIndexMap):
    restb = {}
    for target in CDG.keys():
        restb = get_resource(CDG, DDG, GDDG, fileIndexMap, target, restb)
    return restb


def get_resourceTable_ninja(CDG, DDG, GDDG, fileIndexMap):
    restb = {}
    for target in CDG.keys():
        restb = get_resource_ninja(CDG, DDG, GDDG, fileIndexMap, target, restb)
    return restb


def file_filter(filename, filterdirs):
    normalized_filename = os.path.normpath(filename)
    for dir in filterdirs:
        normalized_filename = os.path.normpath(filename)
        if (normalized_filename.startswith("/")):
            if (normalized_filename.lstrip("/").startswith(dir.lstrip("/"))):
                return False
    return True
    

def dict_filter(dic, filterdirs):
    newdict = {}
    for key in dic.keys():
        if (file_filter(key, filterdirs)):
            newdict[key] = dic[key]
    return newdict


def list_filter(ls, filterdirs):
    newls = []
    for f in ls:
        if (file_filter(f, filterdirs)):
            newls.append(f)
    return newls


def CDG_sharper(CDG):
    filterdirs = get_filterfiles()
    shortCDG = {}
    for target in CDG.keys():
        shortCDG[target] = list_filter(CDG[target], filterdirs)
    return shortCDG


def DDG_sharper(DDG):
    filterdirs = get_filterfiles()
    shortDDG = {}
    for target in DDG.keys():
        shortDDG[target] = {}
        shortDDG[target]['input'] = dict_filter(DDG[target]['input'], filterdirs)
        shortDDG[target]['output'] = dict_filter(DDG[target]['output'], filterdirs)
        shortDDG[target]['create'] = dict_filter(DDG[target]['create'], filterdirs)
        shortDDG[target]['delete'] = dict_filter(DDG[target]['delete'], filterdirs)
    return shortDDG


def DDG_filler(CDG, DDG, fileIndexMap):
    tmpDDG = {}
    for target in DDG.keys():
        tmpDDG[target] = DDG[target]
    for target in CDG.keys():
        if (target in fileIndexMap.keys()):
            tmpDDG[target] = {}
            tmpDDG[target]["input"] = {fileIndexMap[target]: None}
            tmpDDG[target]["output"] = {fileIndexMap[target]: None}
            tmpDDG[target]["create"] = {}
            tmpDDG[target]["delete"] = {}
        elif (not target in DDG.keys()):
            tmpDDG[target] = {}
            tmpDDG[target]["input"] = {}
            tmpDDG[target]["output"] = {}
            tmpDDG[target]["create"] = {}
            tmpDDG[target]["delete"] = {}
    return tmpDDG


def get_pseudotarget(DDG):
    pseudotarget_list = []
    for target in DDG.keys():
        if (DDG[target]["input"] == {} and DDG[target]["output"] == {} and DDG[target]["create"] == {} and DDG[target]["delete"] == {}):
            pseudotarget_list.append(target)
    return pseudotarget_list


def get_childRelationMatrix(CDG):
    relationMatrix = {}
    for target in CDG.keys():
        relationMatrix[target] = {}
        for pre in CDG.keys():
            if (pre == target):
                relationMatrix[target][pre] = True
                continue
            if (pre in CDG[target]):
                relationMatrix[target][pre] = True
            else:
                relationMatrix[target][pre] = False
    return relationMatrix


def get_childRelationMatrixClosure(CDG):
    relationMatrix = get_childRelationMatrix(CDG)
    noleaf = []
    for target in CDG.keys():
        if (CDG[target] == []):
            continue
        else:
            noleaf.append(target)
    print(len(noleaf))
    print(len(set(CDG.keys())))

    count = 1
    for target1 in noleaf:
        print(str(count) + "  /   " + str(len(noleaf)))
        count += 1
        for target2 in relationMatrix.keys():
            if relationMatrix[target1][target2]:
                continue
            for target3 in noleaf:
                if (relationMatrix[target1][target3] and relationMatrix[target3][target2]):
                    relationMatrix[target1][target2] = True
    return relationMatrix


def childRelation_checker(target, subtarget, CDG):
    if (target == subtarget):
        return True
    else:
        childtargetlist = CDG[target]
        if (childtargetlist == []):
            return False
        else:
            childRelation = False
            for childtarget in childtargetlist:
                childRelation = childRelation and childRelation_checker(childtarget, subtarget, CDG)
            return childRelation


def get_succtargets(pre, CDG):
    succtarlist = []
    for target in CDG.keys():
        if (pre in CDG[target]):
            succtarlist.append(target)
    return succtarlist


def echo(shortCDG, shortDDG, resb, outputpath):
    file1 = open(outputpath +'/shortCDG.json', 'w')
    json.dump(shortCDG, file1, indent=4)
    file2 = open(outputpath +'/shortDDG.json', 'w')
    json.dump(shortDDG, file2, indent=4)
    file3 = open(outputpath +'/resource.json', 'w')
    json.dump(resb, file3, indent=4)

    
def echocache(CDG, DDG, fileIndexMap, target2code_map, target2dir_map, outputpath):
    file1 = open(outputpath +'/originCDG.json', 'w')
    json.dump(CDG, file1, indent=4)
    file2 = open(outputpath +'/originDDG.json', 'w')
    json.dump(DDG, file2, indent=4)
    file3 = open(outputpath +'/fileIndex.json', 'w')
    json.dump(fileIndexMap, file3, indent=4)
    file4 = open(outputpath +'/target2code_map.json', 'w')
    json.dump(target2code_map, file4, indent=4)
    file5 = open(outputpath +'/target2dir_map.json', 'w')
    json.dump(target2dir_map, file5, indent=4)


def echocache_ninja(CDG, DDG, fileIndexMap, outputpath):
    file1 = open(outputpath + '/originCDG.json', 'w')
    json.dump(CDG, file1, indent=4)
    file2 = open(outputpath + '/originDDG.json', 'w')
    json.dump(DDG, file2, indent=4)
    file3 = open(outputpath + '/fileIndex.json', 'w')
    json.dump(fileIndexMap, file3, indent=4)


def echotime(pre_time, CDG_time, DDG_time, res_time, MP_time, EP_time, FT_time, FR_time, IC_time, total_time, outputpath):
    time_rec = {}
    time_rec["Total"] = total_time
    time_rec["prepare"] = pre_time
    time_rec["CDG_time"] = CDG_time
    time_rec["DDG_time"] = DDG_time
    time_rec["res_time"] = res_time
    time_rec["MP"] = MP_time
    time_rec["EP"] = EP_time
    time_rec["FT"] = FT_time
    time_rec["FR"] = FR_time
    time_rec["IC"] = IC_time
    tfile = open(outputpath + '/time.json', 'w')
    json.dump(time_rec, tfile, indent=4)


def loadCache(outputpath):
    file1 = open(outputpath + "/originCDG.json",'r+')
    CDG = eval(file1.read())
    file2 = open(outputpath + "/originDDG.json",'r+')
    DDG = eval(file2.read())
    file3 = open(outputpath +'/fileIndex.json', 'r+')
    fileIndexMap = eval(file3.read())
    file4 = open(outputpath +'/target2code_map.json', 'r+')
    target2code_map = eval(file4.read())
    file5 = open(outputpath +'/target2dir_map.json', 'r+')
    target2dir_map = eval(file5.read())
    return CDG, DDG, fileIndexMap, target2code_map, target2dir_map


def loadCache_ninja(outputpath):
    file1 = open(outputpath + "/originCDG.json",'r+')
    CDG = eval(file1.read())
    file2 = open(outputpath + "/originDDG.json",'r+')
    DDG = eval(file2.read())
    file3 = open(outputpath +'/fileIndex.json', 'r+')
    fileIndexMap = eval(file3.read())
    return CDG, DDG, fileIndexMap


def loadReport_ninja(outputpath):
    file1 = open(outputpath + '/MP.json', 'r+')
    MP_report = eval(file1.read())
    file2 = open(outputpath + '/EP.json', 'r+')
    EP_report = eval(file2.read())
    return MP_report, EP_report


def loadReport(outputpath, detectIssues):
    MP_report = None
    EP_report = None
    FT_report = None
    FR_report = None
    IC_report = None
    
    if (detectIssues["MP"]):
        file1 = open(outputpath + '/MP.json', 'r+')
        MP_report = eval(file1.read())
    
    if (detectIssues["EP"]):
        file2 = open(outputpath + '/EP.json', 'r+')
        EP_report = eval(file2.read())
    
    if (detectIssues["FT"]):
        file3 = open(outputpath + '/FT.json', 'r+')
        FT_report = eval(file3.read())
    
    if (detectIssues["FR"]):
        file4 = open(outputpath + '/FR.json', 'r+')
        FR_report = eval(file4.read())

    if (detectIssues["IC"]):
        IC_file = outputpath + '/IC.json'

        try:
            file5 = open(IC_file, 'r+')
            IC_report = eval(file5.read())
        except Exception as e: 
            print("Could not find %s" % (IC_file))
            IC_report = None
    
    return MP_report, EP_report, FT_report, FR_report, IC_report


                
    

