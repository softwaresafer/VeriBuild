import io
import sys
import os
import json
import copy
import time
from VeMakeDDG.DDG import *
from VeMakeCDG.CDG import *
from parse import *
from Util.operation import loadCache
from Util.operation import loadReport
from Validator.MP_validator import *


def generate_DGdiagsteps(CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, srcfiles, outputpath, target):
    diagstepCDG = {}
    if (target in CDGLineNumber.keys()):
        diagstepCDG["Line"] = CDGLineNumber[target] - 1
        diagstepCDG["File"] =  srcfiles.index(outputpath + "/originCDG.json")
        diagstepCDG["Tip"] = "the expected prerequisites of " + target + " (originCDG)"
        diagstepCDG["RawTip"] = diagstepCDG["Tip"]

    diagstepDDG = {}
    if (target in DDGLineNumber.keys()):
        diagstepDDG["Line"] = DDGLineNumber[target] - 1
        diagstepDDG["File"] =  srcfiles.index(outputpath + "/originDDG.json")
        diagstepDDG["Tip"] = "IO info of " + target + " (originDDG)"
        diagstepDDG["RawTip"] = diagstepDDG["Tip"]

    diagstepShortCDG = {}
    if (target in CDGLineNumber.keys()):
        diagstepShortCDG["Line"] = shortCDGLineNumber[target] - 1
        diagstepShortCDG["File"] =  srcfiles.index(outputpath + "/shortCDG.json")
        diagstepShortCDG["Tip"] = "the expected prerequisites of " + target + " (shortCDG)"
        diagstepShortCDG["RawTip"] = diagstepShortCDG["Tip"]

    diagstepShortDDG = {}
    if (target in DDGLineNumber.keys()):
        diagstepShortDDG["Line"] = shortDDGLineNumber[target] - 1
        diagstepShortDDG["File"] =  srcfiles.index(outputpath + "/shortDDG.json")
        diagstepShortDDG["Tip"] = "IO info of " + target + " (shortDDG)"
        diagstepShortDDG["RawTip"] = diagstepShortDDG["Tip"]

    return diagstepCDG, diagstepDDG, diagstepShortCDG, diagstepShortDDG


def MP_reportor(vmreport, srcfiles, filepath, outputpath, isTouchMode, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map, MP, MP_fileMap):
    MP_report = {}
    MP_report["Name"] = "Missing Prerequisites"
    MP_report["Descripition-En"] = "Missing Prerequisites"
    MP_report["Description"] = "MP"
    MP_report["Reports"] = []

    #Touch Mode
    TrueMP_report = {}
    TrueMP_report["Name"] = "Missing Prerequisites(True Bug)"
    TrueMP_report["Descripition-En"] = "Missing Prerequisites(True Bug)"
    TrueMP_report["Description"] = "MP(True Bug)"
    TrueMP_report["Reports"] = []

    FalseMP_report = {}
    FalseMP_report["Name"] = "Missing Prerequisites(False Bug)"
    FalseMP_report["Descripition-En"] = "Missing Prerequisites(False Bug)"
    FalseMP_report["Description"] = "MP(False Bug)"
    FalseMP_report["Reports"] = []

    TrueMP = {}
    # do not execute for ninja
    # if (isTouchMode):
    #     TrueMP = MP_validator(filepath, "default", MP)

    # Add MP report
    for target in MP.keys():
        if MP[target]["Missing Prerequisites"] == []:
            continue
        singleReport = {}
        singleReport["Score"] = 100
        singleReport["ReportChecker"] = "Vemake MP checker"
        singleReport["Valid"] = True
        singleReport["Dominated"] = False
        singleReport["DiagSteps"] = []
        if (target in target2code_map.keys()):
            fileList, lineNums = get_CmdInfo(target2code_map[target])
            if (fileList == []):
                diagstep = {}
                diagstep["Line"] = 0
                if (srcfiles.index(filepath + "/Makefile") != -1):
                    diagstep["File"] = srcfiles.index(filepath + "/Makefile")
                else:
                    diagstep["File"] = srcfiles.index(filepath + "/makefile")
                diagstep["Tip"] = target + " (MP)"
                diagstep["RawTip"] = diagstep["Tip"]
                singleReport["DiagSteps"].append(diagstep)
            for i in range(len(fileList)):
                diagstep1 = {}
                diagstep1["Line"] = lineNums[i] - 1
                if ((target2dir_map[target] + "/" + fileList[i]) in srcfiles):
                    diagstep1["File"] = srcfiles.index(target2dir_map[target] + "/" + fileList[i])
                    diagstep1["Tip"] = target + " (MP)"
                    diagstep1["RawTip"] = diagstep1["Tip"]
                    singleReport["DiagSteps"].append(diagstep1)
            
        profilediagstep = {}
        if (target in profileLineNumber.keys()):
            profilediagstep["Line"] = profileLineNumber[target]
        else:
            profilediagstep["Line"] = 0

        profilediagstep["File"] = srcfiles.index(filepath + "/profile.txt")
        profilediagstep["Tip"] = "profile of Make"
        profilediagstep["RawTip"] = profilediagstep["Tip"]
        singleReport["DiagSteps"].append(profilediagstep)   

        resultdetails = {}
        resultdetails["Line"] = 0
        resultFileIndex = MP_fileMap[target]
        resultdetails["File"] = srcfiles.index(outputpath + "/MP_" + str(resultFileIndex) + ".json")
        resultdetails["Tip"] = "Read single report file for detailed description"
        resultdetails["RawTip"] = resultdetails["Tip"]
        singleReport["DiagSteps"].append(resultdetails)

        diagstepCDG, diagstepDDG, diagstepShortCDG, diagstepShortDDG = generate_DGdiagsteps(CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, srcfiles, outputpath, target)
        singleReport["DiagSteps"].append(diagstepCDG)
        singleReport["DiagSteps"].append(diagstepDDG)
        singleReport["DiagSteps"].append(diagstepShortCDG)
        singleReport["DiagSteps"].append(diagstepShortDDG)

        if (not isTouchMode):
            MP_report["Reports"].append(singleReport)
        else:
            if (target in TrueMP.keys()):
                TrueMP_report["Reports"].append(singleReport)
            else:
                FalseMP_report["Reports"].append(singleReport)

    vmreport["BugTypes"].append(MP_report)
    vmreport["BugTypes"].append(TrueMP_report)
    vmreport["BugTypes"].append(FalseMP_report)
    return vmreport


def EP_reportor(vmreport, srcfiles, filepath, outputpath, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map, EP, EP_fileMap):
    EP_report = {}
    EP_report["Name"] = "Excessive Prerequisites"
    EP_report["Descripition-En"] = "Excessive Prerequisites"
    EP_report["Description"] = "EP"
    EP_report["Reports"] = []

    for target in EP.keys():
        if EP[target]["Excessive Prerequisites"] == []:
            continue
        singleReport = {}
        singleReport["Score"] = 100
        singleReport["ReportChecker"] = "Vemake EP checker"
        singleReport["Valid"] = True
        singleReport["Dominated"] = False
        singleReport["DiagSteps"] = []
        if (target in target2code_map.keys()):
            fileList, lineNums = get_CmdInfo(target2code_map[target])
            if (fileList == []):
                diagstep = {}
                diagstep["Line"] = 0
                if (srcfiles.index(filepath + "/Makefile") != -1):
                    diagstep["File"] = srcfiles.index(filepath + "/Makefile")
                else:
                    diagstep["File"] = srcfiles.index(filepath + "/makefile")
                diagstep["Tip"] = target + " (EP)"
                diagstep["RawTip"] = diagstep["Tip"]
                singleReport["DiagSteps"].append(diagstep)
            for i in range(len(fileList)):
                diagstep1 = {}
                diagstep1["Line"] = lineNums[i] - 1
                if ((target2dir_map[target] + "/" + fileList[i]) in srcfiles):
                    diagstep1["File"] = srcfiles.index(target2dir_map[target] + "/" + fileList[i])
                    diagstep1["Tip"] = target + " (EP)"
                    diagstep1["RawTip"] = diagstep1["Tip"]
                    singleReport["DiagSteps"].append(diagstep1)

        profilediagstep = {}
        if (target in profileLineNumber.keys()):
            profilediagstep["Line"] = profileLineNumber[target]
        else:
            profilediagstep["Line"] = 0
        profilediagstep["File"] = srcfiles.index(filepath + "/profile.txt")
        profilediagstep["Tip"] = "profile of Make"
        profilediagstep["RawTip"] = profilediagstep["Tip"]
        singleReport["DiagSteps"].append(profilediagstep) 
        for prerequisite in EP[target]["Excessive Prerequisites"]:
            diagstepCDG, diagstepDDG, diagstepShortCDG, diagstepShortDDG = generate_DGdiagsteps(CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, srcfiles, outputpath, prerequisite)
            if (list(diagstepDDG.keys()) != []):
                singleReport["DiagSteps"].append(diagstepDDG)
                singleReport["DiagSteps"].append(diagstepShortDDG)

        resultdetails = {}
        resultdetails["Line"] = 0
        resultFileIndex = EP_fileMap[target]
        resultdetails["File"] = srcfiles.index(outputpath + "/EP_" + str(resultFileIndex) + ".json")
        resultdetails["Tip"] = "Read single report file for detailed description"
        resultdetails["RawTip"] = resultdetails["Tip"]
        singleReport["DiagSteps"].append(resultdetails)

        diagstepCDG, diagstepDDG, diagstepShortCDG, diagstepShortDDG = generate_DGdiagsteps(CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, srcfiles, outputpath, target)
        singleReport["DiagSteps"].append(diagstepCDG)
        singleReport["DiagSteps"].append(diagstepDDG)
        singleReport["DiagSteps"].append(diagstepShortCDG)
        singleReport["DiagSteps"].append(diagstepShortDDG)
        EP_report["Reports"].append(singleReport)

    vmreport["BugTypes"].append(EP_report)
    return vmreport


def FT_reportor(vmreport, srcfiles, filepath, outputpath, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map, FT, FT_fileMap):
    FT_report = {}
    FT_report["Name"] = "File-Target Inconsistency"
    FT_report["Descripition-En"] = "File-Target Inconsistency"
    FT_report["Description"] = "FT"
    FT_report["Reports"] = []

    for target in FT.keys():
        if FT[target]["File-Target Inconsistency"] == []:
            continue
        singleReport = {}
        singleReport["Score"] = 100
        singleReport["ReportChecker"] = "Vemake FT checker"
        singleReport["Valid"] = True
        singleReport["Dominated"] = False
        singleReport["DiagSteps"] = []
        if (target in target2code_map.keys()):
            fileList, lineNums = get_CmdInfo(target2code_map[target])
            if (fileList == []):
                diagstep = {}
                diagstep["Line"] = 0
                if (srcfiles.index(filepath + "/Makefile") != -1):
                    diagstep["File"] = srcfiles.index(filepath + "/Makefile")
                else:
                    diagstep["File"] = srcfiles.index(filepath + "/makefile")
                diagstep["Tip"] = target + " (FT)"
                diagstep["RawTip"] = diagstep["Tip"]
                singleReport["DiagSteps"].append(diagstep)
            for i in range(len(fileList)):
                diagstep1 = {}
                diagstep1["Line"] = lineNums[i] - 1
                if ((target2dir_map[target] + "/" + fileList[i]) in srcfiles):
                    diagstep1["File"] = srcfiles.index(target2dir_map[target] + "/" + fileList[i])
                    diagstep1["Tip"] = target + " (FT)"
                    diagstep1["RawTip"] = diagstep1["Tip"]
                    singleReport["DiagSteps"].append(diagstep1)

        profilediagstep = {}
        if (target in profileLineNumber.keys()):
            profilediagstep["Line"] = profileLineNumber[target]
        else:
            profilediagstep["Line"] = 0
        profilediagstep["File"] = srcfiles.index(filepath + "/profile.txt")
        profilediagstep["Tip"] = "profile of Make"
        profilediagstep["RawTip"] = profilediagstep["Tip"]
        singleReport["DiagSteps"].append(profilediagstep) 
        for prerequisite in FT[target]["File-Target Inconsistency"]:
            diagstepCDG, diagstepDDG, diagstepShortCDG, diagstepShortDDG = generate_DGdiagsteps(CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, srcfiles, outputpath, prerequisite)
            if (list(diagstepDDG.keys()) != []):
                singleReport["DiagSteps"].append(diagstepDDG)
                singleReport["DiagSteps"].append(diagstepShortDDG)

        resultdetails = {}
        resultdetails["Line"] = 0
        resultFileIndex = FT_fileMap[target]
        resultdetails["File"] = srcfiles.index(outputpath + "/FT_" + str(resultFileIndex) + ".json")
        resultdetails["Tip"] = "Read single report file for detailed description"
        resultdetails["RawTip"] = resultdetails["Tip"]
        singleReport["DiagSteps"].append(resultdetails)

        diagstepCDG, diagstepDDG, diagstepShortCDG, diagstepShortDDG = generate_DGdiagsteps(CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, srcfiles, outputpath, target)
        singleReport["DiagSteps"].append(diagstepCDG)
        singleReport["DiagSteps"].append(diagstepDDG)
        singleReport["DiagSteps"].append(diagstepShortCDG)
        singleReport["DiagSteps"].append(diagstepShortDDG)
        FT_report["Reports"].append(singleReport)

    vmreport["BugTypes"].append(FT_report)
    return vmreport


def FR_reportor(vmreport, srcfiles, filepath, outputpath, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map, FR, FR_result):
    FR_report = {}
    FR_report["Name"] = "File Race"
    FR_report["Descripition-En"] = "File Race"
    FR_report["Description"] = "FR"
    FR_report["Reports"] = []


    for FRtype in FR_result.keys():
        for FRpair in FR_result[FRtype]:
            singleReport = {}
            singleReport["Score"] = 100
            singleReport["ReportChecker"] = "Vemake FR checker"
            singleReport["Valid"] = True
            singleReport["Dominated"] = False
            singleReport["DiagSteps"] = []

            resultdetails = {}
            resultdetails["Line"] = 0
            resultdetails["File"] = srcfiles.index(outputpath + "/FR.json")
            resultdetails["Tip"] = FRtype + "\n" + FRpair[0] + "\n" + FRpair[1]
            resultdetails["RawTip"] = resultdetails["Tip"]
            singleReport["DiagSteps"].append(resultdetails)

            for target in FRpair:
                if (target in target2code_map.keys()):
                    fileList, lineNums = get_CmdInfo(target2code_map[target])
                    if (fileList == []):
                        diagstep = {}
                        diagstep["Line"] = 0
                        if (srcfiles.index(filepath + "/Makefile") != -1):
                            diagstep["File"] = srcfiles.index(filepath + "/Makefile")
                        else:
                            diagstep["File"] = srcfiles.index(filepath + "/makefile")
                        diagstep["Tip"] = target + " (FR)"
                        diagstep["RawTip"] = diagstep["Tip"]
                        singleReport["DiagSteps"].append(diagstep)
                    for i in range(len(fileList)):
                        diagstep1 = {}
                        diagstep1["Line"] = lineNums[i] - 1
                        if ((target2dir_map[target] + "/" + fileList[i]) in srcfiles):
                            diagstep1["File"] = srcfiles.index(target2dir_map[target] + "/" + fileList[i])
                            diagstep1["Tip"] = target + " (FR)"
                            diagstep1["RawTip"] = diagstep1["Tip"]
                            singleReport["DiagSteps"].append(diagstep1)

                profilediagstep = {}
                if (target in profileLineNumber.keys()):
                    profilediagstep["Line"] = profileLineNumber[target]
                else:
                    profilediagstep["Line"] = 0
                profilediagstep["File"] = srcfiles.index(filepath + "/profile.txt")
                profilediagstep["Tip"] = "profile of Make"
                profilediagstep["RawTip"] = profilediagstep["Tip"]
                singleReport["DiagSteps"].append(profilediagstep) 

                diagstepCDG, diagstepDDG, diagstepShortCDG, diagstepShortDDG = generate_DGdiagsteps(CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, srcfiles, outputpath, target)
                singleReport["DiagSteps"].append(diagstepCDG)
                singleReport["DiagSteps"].append(diagstepDDG)
                singleReport["DiagSteps"].append(diagstepShortCDG)
                singleReport["DiagSteps"].append(diagstepShortDDG)

            FR_report["Reports"].append(singleReport)

    vmreport["BugTypes"].append(FR_report)
    return vmreport


def IC_reportor(vmreport, srcfiles, filepath, outputpath, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map, IC):
    if (IC["created_files"] == [] and IC["deleted_files"] == []):
        return vmreport

    IC_report = {}
    IC_report["Name"] = "Inconsistent Clean"
    IC_report["Descripition-En"] = "Inconsistent Clean"
    IC_report["Description"] = "IC"
    IC_report["Reports"] = []

    singleReport = {}
    singleReport["Score"] = 100
    singleReport["ReportChecker"] = "Vemake IC checker"
    singleReport["Valid"] = True
    singleReport["Dominated"] = False
    singleReport["DiagSteps"] = []
    fileList, lineNums = get_CmdInfo(target2code_map["clean"])
    if (fileList == []):
        diagstep = {}
        diagstep["Line"] = 0
        if (srcfiles.index(filepath + "/Makefile") != -1):
            diagstep["File"] = srcfiles.index(filepath + "/Makefile")
        else:
            diagstep["File"] = srcfiles.index(filepath + "/makefile")
        diagstep["Tip"] = "(IC)"
        diagstep["RawTip"] = diagstep["Tip"]
        singleReport["DiagSteps"].append(diagstep)
    for i in range(len(fileList)):
        diagstep1 = {}
        diagstep1["Line"] = lineNums[i] - 1
        if ((target2dir_map["clean"] + "/" + fileList[i]) in srcfiles):
            diagstep1["File"] = srcfiles.index(target2dir_map["clean"] + "/" + fileList[i])
            diagstep1["Tip"] = "Read report description for details"
            diagstep1["RawTip"] = diagstep1["Tip"]
            singleReport["DiagSteps"].append(diagstep1)
        diagstep2 = {}
        diagstep2["Line"] = lineNums[i] - 1
        if ((target2dir_map["clean"] + "/" + fileList[i]) in srcfiles):
            diagstep2["File"] = srcfiles.index(target2dir_map["clean"] + "/" + fileList[i])
            diagstep2["Tip"] = "Read report description for details"
            diagstep2["RawTip"] = diagstep2["Tip"]
            singleReport["DiagSteps"].append(diagstep2)
    profilediagstep = {}
    if ("clean" in profileLineNumber.keys()):
        profilediagstep["Line"] = profileLineNumber["clean"]
    else:
        profilediagstep["Line"] = 0
    profilediagstep["File"] = srcfiles.index(filepath + "/profile.txt")
    profilediagstep["Tip"] = "(IC)"
    profilediagstep["RawTip"] = profilediagstep["Tip"]
    singleReport["DiagSteps"].append(profilediagstep) 

    IC_report["Reports"].append(singleReport)
    vmreport["BugTypes"].append(IC_report)
    return vmreport


def time_reportor(vmreport, srcfiles, filepath, outputpath, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map):
    T_report = {}
    T_report["Name"] = "Time Cost"
    T_report["Descripition-En"] = "Time Cost"
    T_report["Description"] = "Time Cost"
    T_report["Reports"] = []

    singleReport = {}
    singleReport["Score"] = 0
    singleReport["ReportChecker"] = "Vemake Time Cost"
    singleReport["Valid"] = True
    singleReport["Dominated"] = False
    singleReport["DiagSteps"] = []

    diagstep = {}
    diagstep["Line"] = 0
    diagstep["File"] = srcfiles.index(outputpath + "/time.json")
    diagstep["Tip"] = "Time Cost"
    diagstep["RawTip"] = diagstep["Tip"]
    singleReport["DiagSteps"].append(diagstep)

    T_report["Reports"].append(singleReport)
    vmreport["BugTypes"].append(T_report)
    return vmreport


def generate_reportor(filepath, outputpath, isTouchMode, detectIssues, MP_fileMap, EP_fileMap, FT_fileMap, FR_result, IC_result):
    time_start = time.time()
    vmreport = {}
    srcfiles = []
    srcfiles.extend(iter_files(filepath))
    srcfiles.extend(iter_files(outputpath))

    # import data from jsons
    CDG, DDG, fileIndexMap, target2code_map, target2dir_map = loadCache(outputpath)
    MP, EP, FT, FR, IC = loadReport(outputpath, detectIssues)

    CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber = get_DG_targetLineNum(outputpath)
    profileLineNumber = get_profile_targetLineNumber(filepath, CDG)

    # construct the vemake report
    vmreport["SrcFiles"] = srcfiles
    vmreport["BugTypes"] = []

    # MP EP FT FR IC report
    if (detectIssues["MP"]):
        vmreport = MP_reportor(vmreport, srcfiles, filepath, outputpath, isTouchMode, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map, MP, MP_fileMap)
    if (detectIssues["EP"]):
        vmreport = EP_reportor(vmreport, srcfiles, filepath, outputpath, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map, EP, EP_fileMap)
    if (detectIssues["FT"]):
        vmreport = FT_reportor(vmreport, srcfiles, filepath, outputpath, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map, FT, FT_fileMap)
    if (detectIssues["FR"]):
        vmreport = FR_reportor(vmreport, srcfiles, filepath, outputpath, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map, FR, FR_result)
    if (detectIssues["IC"]):
        vmreport = IC_reportor(vmreport, srcfiles, filepath, outputpath, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map, IC)

    vmreport = time_reportor(vmreport, srcfiles, filepath, outputpath, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map)
    filep = open(outputpath + '/vmreport.json', 'w')
    json.dump(vmreport, filep, indent=4)

    time_end = time.time()
    return (time_end - time_start)


def generate_reportor_ninja(filepath, outputpath, isTouchMode, detectIssues, MP_fileMap, EP_fileMap):
    time_start = time.time()
    vmreport = {}
    srcfiles = []
    srcfiles.extend(iter_files(filepath))
    srcfiles.extend(iter_files(outputpath))

    # import data from jsons
    CDG, DDG, fileIndexMap = loadCache_ninja(outputpath)
    MP, EP, FT, FR, IC = loadReport(outputpath)

    CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber = get_DG_targetLineNum(outputpath)
    profileLineNumber = get_profile_targetLineNumber(filepath, CDG)

    # construct the vemake report
    vmreport["SrcFiles"] = srcfiles
    vmreport["BugTypes"] = []

    # MP EP report
    if detectIssues["MP"]:
        vmreport = MP_reportor(vmreport, srcfiles, filepath, outputpath, isTouchMode, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map, MP, MP_fileMap)
    if detectIssues["EP"]:
        vmreport = EP_reportor(vmreport, srcfiles, filepath, outputpath, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map, EP, EP_fileMap)

    vmreport = time_reportor(vmreport, srcfiles, filepath, outputpath, profileLineNumber, CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber, fileIndexMap, target2code_map, target2dir_map)
    filep = open(outputpath + '/vmreport.json', 'w')
    json.dump(vmreport, filep, indent=4)

    time_end = time.time()
    return (time_end - time_start)
