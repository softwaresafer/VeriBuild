import io
import os
import sys
import json
import time
import networkx as nx
from VeMakeCDG.CDG import get_CDG
from VeMakeDDG.DDG import get_DDG
from Util.operation import *
from Util.parser import *
from Util.reportor import *
from Detector.IC_detector import *
from Detector.EP_detector import *
from Detector.MP_detector import *
from Detector.FR_detector import *
from Detector.FT_detector import *
from VeMakeTrace.preprocess import *
from Validator.MP_validator import *
from Validator.compare_validator import *


def singlerun(filepath, outputdir, execmethod, cleanmethod, touchmethod, detectIssue, jnum, isSimplified):
    time_total_start = time.time()
    project_name = filepath.rsplit('/')[-1]
    outputpath = outputdir + "/" + project_name
    toptargets = []
    if not os.path.exists(outputpath):
        os.makedirs(outputpath)
    G = nx.DiGraph()

    time_CDG_finished = 0
    time_DDG_finished = 0
    CDG_time = 0
    DDG_time = 0
    res_time = 0

    if (execmethod == "-cache"):
        CDG, DDG, fileIndexMap, target2code_map, target2dir_map = loadCache(outputpath)
        edges_list = [((node, nbr)) for node, nbrlist in CDG.items() for nbr in nbrlist]
        G.add_edges_from(edges_list)
        toptargets = list(filter(lambda node: G.in_degree(node) == 0, list(G.nodes())))
        print(toptargets)
    else:
        CDG, target_sequence, target2code_map, target2dir_map, fileIndexMap = get_CDG(filepath, cleanmethod, jnum)
        print("CDG construction finished")
        edges_list = [((node, nbr)) for node, nbrlist in CDG.items() for nbr in nbrlist]
        G.add_edges_from(edges_list)
        toptargets = []
        if (isSimplified):
            toptargets.append("")
        else:
            toptargets = list(filter(lambda node: G.in_degree(node) == 0, list(G.nodes())))
        time_CDG_finished = time.time()
        CDG_time = time_CDG_finished - time_total_start

        DDG, pidtarget_map = get_DDG(filepath, toptargets, cleanmethod, jnum)
        print("DDG construction finished")
        time_DDG_finished = time.time()
        DDG_time = time_DDG_finished - time_CDG_finished
        
        echocache(CDG, DDG, fileIndexMap, target2code_map, target2dir_map, outputpath)


    time_start = time.time()
    shortCDG = CDG_sharper(CDG)
    print("CDG sharper finished")
    shortDDG = DDG_sharper(DDG)
    print("DDG sharper finished")
    DDG = DDG_filler(CDG, DDG, fileIndexMap)
    print("DDG filler finished")
    GDDG = get_GDDG(CDG, DDG)
    print("GDDG construction finished")
    restb = get_resourceTable(CDG, DDG, GDDG, fileIndexMap)
    print("Resource table construction finished")
    time_end = time.time()
    pre_time = time_end - time_total_start
    res_time = time_end - time_DDG_finished

    echo(shortCDG, shortDDG, restb, outputpath)

    MP_time = 0
    MP_fileMap = {}  
    EP_time = 0
    EP_fileMap = {}
    FT_time = 0
    FT_fileMap = {}
    FR_time = 0
    FR_fileMap = {}
    FR_result = {}
    IC_time = 0
    IC_result = {}
    
    if (detectIssue["MP"]):
        MP_time, MP_fileMap, MP_result = MP_detect(CDG, DDG, restb, fileIndexMap, outputpath)
        print("MP detection finished")
    if (detectIssue["EP"]):
        EP_time, EP_fileMap, EP_result = EP_detect(CDG, DDG, restb, fileIndexMap, outputpath)
        print("EP detection finished")
    if (detectIssue["FT"]):
        FT_time, FT_fileMap, FT_result = FT_detect(G, CDG, DDG, target2dir_map, fileIndexMap, outputpath)
        print("FT detection finished")
    if (detectIssue["FR"]):
        FR_time, FR_result = FR_detect(G, CDG, shortDDG, fileIndexMap, outputpath)
        print("FR detection finished")
    if (detectIssue["IC"]):
        IC_time, IC_result = IC_detecor(filepath, outputpath, cleanmethod, jnum)
        print("IC detection finished")

    if (touchmethod == "-touch"):
        MP_Truebugs = MP_validator(filepath, cleanmethod, MP_result)
        print(len(MP_Truebugs))

    time_total_end = time.time()
    total_time = time_total_end - time_total_start
    echotime(pre_time, CDG_time, DDG_time, res_time, MP_time, EP_time, FT_time, FR_time, IC_time, total_time, outputpath)
    print("pre_time" + str(pre_time))
    print("CDG time" + str(CDG_time))
    print("DDG time" + str(DDG_time))
    print("res time" + str(res_time))
    print("MP_time " + str(MP_time))
    print("EP_time " + str(EP_time))
    print("FT_time " + str(FT_time))
    print("FR_time " + str(FT_time))
    VMReport_time = generate_reportor(filepath, outputpath, touchmethod == "-touch", detectIssue, MP_fileMap, EP_fileMap, FT_fileMap, FR_result, IC_result)

    # compare with mkcheck
    # compare_run(project_name)
    return toptargets


def batchrun(filepath, outputdir, execmethod, cleanmethod, touchmethod, detectIssue, jnum, isSimplified):
    project_name = filepath.rsplit('/')[-1]
    outputpath = outputdir + "/" + project_name
    print(project_name)
    commitIDList = get_commitIDList(project_name)

    for commitID in commitIDList:
        path = os.getcwd()
        os.chdir(filepath)
        os.system("git checkout " + commitID)
        os.chdir(path)
        singlerun(filepath, outputdir, execmethod, cleanmethod, touchmethod, detectIssue, jnum, isSimplified)
        os.chdir(filepath)
        reportname = "vemake_" + project_name + "_" + commitID[:8]
        os.system("pp-capture --capture-only --run-index -- make")
        os.system("pp-report --remote localhost --remote-port 40088 --upload " + reportname + " --user adminuser --passwd vemaketest --builddir . --allow-invalid-types ../../testoutput/" + project_name + "/vmreport.json")
        os.system("git clean -fdx - e .piggy")
        os.system("git checkout .")
        os.system("git checkout -")
        os.chdir(path)
    print("Batch test finished: " + str(len(commitIDList)) + " commits")
    return


if __name__ == "__main__":
    jnum = 1
    validoption = True
    filepath_list = []

    if ("-j" in sys.argv[1:]):
        if sys.argv[-1] == "-j":
            validoption = False
        else:
            jnum = int(sys.argv[-1])

    if (not validoption):
        print("option error")
    elif((not (set(filter(lambda op: op.startswith("-"), sys.argv[1:]))).issubset(set(["-j", "-simple", "-config", "-batch", "-f", "-configure", "-onlytouch", "-touch", "-trace", "-cache", "-MP", "-EP", "-FT", "-FR", "-IC"]))) or (("-config" in sys.argv[1:]) and ("-configure" in sys.argv[1:]))):
        print("option error")
    else:
        if ("-f" in sys.argv[1:]):
            filepath = sys.argv[sys.argv.index("-f") + 1]
            filepath_list.append(filepath)
        else:
            filepath_list = get_testproject()
        outputdir = get_outputdir()
        for filepath in filepath_list:
            print(filepath + " test starts")
            cleanmethod = "default"
            execmethod = "default"
            touchmethod = "default"
            if ("-config" in sys.argv[1:]):
                cleanmethod = "-config"
            elif ("-configure" in sys.argv[1:]):
                cleanmethod = "-configure"
            if ("-cache" in sys.argv[1:]):
                execmethod = "-cache"
            if ("-touch" in sys.argv[1:]):
                touchmethod = "-touch"
            if ("-onlytouch" in sys.argv[1:]):
                project_name = filepath.rsplit('/')[-1]
                outputpath = outputdir + "/" + project_name
                fileresult = open(outputpath + "/MP.json",'r+')
                MP_result = eval(fileresult.read())
                MP_Truebugs = MP_validator(filepath, cleanmethod, MP_result)
            else:
                detectIssue = {}
                isDefault = (not (("-MP" in sys.argv[1:]) or ("-EP" in sys.argv[1:]) or ("-FT" in sys.argv[1:]) or ("-FR" in sys.argv[1:])))
                detectIssue["MP"] = (("-MP" in sys.argv[1:]) or isDefault)
                detectIssue["EP"] = (("-EP" in sys.argv[1:]) or isDefault)
                detectIssue["FT"] = ("-FT" in sys.argv[1:])
                detectIssue["FR"] = ("-FR" in sys.argv[1:])
                detectIssue["IC"] = False
                # detectIssue["IC"] = ("-IC" in sys.argv[1:])

                # two modes: singlerun, batchrun
                if ("-batch" in sys.argv[1:]):
                    batchrun(filepath, outputdir, execmethod, cleanmethod, touchmethod, detectIssue, jnum, "-simple" in sys.argv[1:])
                else:
                    toptargets = singlerun(filepath, outputdir, execmethod, cleanmethod, touchmethod, detectIssue, jnum, "-simple" in sys.argv[1:])    
                print(filepath + " test finished")
