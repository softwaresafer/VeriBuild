import io
import sys
import os
import configparser
from parse import *
from xml.dom.minidom import parse as libparse
import xml.dom.minidom

def my_normpath(curdir, filename):
    retpath = ""
    if (filename.startswith("/")):
        retpath = "/" + filename.lstrip("/")
    else:
        retpath = "/" + curdir.lstrip("/") + "/" + filename
    return os.path.normpath(retpath)


def get_testproject():
    cf = configparser.ConfigParser()
    cf.read("../config/config.ini")
    return list(filter(lambda c: c != '', cf.get("path", "testproject").split("\n")))


def get_outputdir():
    cf = configparser.ConfigParser()
    cf.read("../config/config.ini")
    return cf.get("path", "outputdir")


def get_commitIDList(projectname):
    cf = configparser.ConfigParser()
    cf.read("../config/config.ini")
    basedir = cf.get("path", "oracleset")
    if (not os.path.exists(basedir + "/" + projectname + ".json")):
        return []
    commitLog = open(basedir + "/" + projectname + ".json",'r+')
    commitInfo = eval(commitLog.read())
    commitIDList = []
    for commit in commitInfo["Missing Prerequsistes"]:
        commitIDList.append(commit["preCommitId"])
    for commit in commitInfo["Excessive Prerequsities"]:
        commitIDList.append(commit["preCommitId"])
    return list(set(commitIDList))


def get_filterfiles():
    cf = configparser.ConfigParser()
    cf.read("../config/config.ini")
    return list(filter(lambda c: c != '', cf.get("config", "filterfiles").split("\n")))


def get_cwd(line):
    format = "{timestamp:tt} chdir(\"{curdir}\"){spacestr1}={spacestr2}{state}"
    r = parse(format, line)
    if (r == None):
        return None
    if ("0" not in r['state']):
        return None
    else:
        return r['curdir']


def get_unlinkedfile(line):
    format = "{timestamp:tt} unlink(\"{filename}\""
    r = parse(format, line.rsplit(")", 1)[0])
    if (r != None):
        return r['filename'], str(r['timestamp'])
    else:
        return None, None


def get_execvefile(line):
    format = "{timestamp:tt} execve(\"{filename}\",{postline}"
    r = parse(format, line)
    if (r == None):
        return None, None, "FAIL"
    if ("ENOENT (No such file or directory)" in r['postline']):
        return None, None, "FAIL"
    else:
        return r['filename'], str(r['timestamp']), "SUCCESS"


def get_openedfile(line):
    format1 = "{timestamp:tt} openat({dirfd}, \"{filename}\", {mode}, {intpara}) = {fd}"
    format2 = "{timestamp:tt} openat({dirfd}, \"{filename}\", {mode}) = {fd}"
    for f in [format1, format2]:
        r1 = parse(f, line)
        if r1:
            filename = r1['filename']
            timestamp = str(r1['timestamp'])
            mode = r1['mode'] 
            fd = r1['fd']
            if "<" in fd:
                    r2 = parse("{fd:d}<{fullpath}>",fd)
                    filename = r2["fullpath"]
            return filename, timestamp, mode
    return None, None, "FAIL" 

def get_initpwd(line):
    index = line.find("\"PWD=")
    if (index != -1):
        tmpline = line[(index + 5):]
        pwd = tmpline[:tmpline.find("\"")]
        return pwd
    else:
        return None

def get_renamedfile(line):
    format = "{timestamp:tt} rename(\"{filename1}\", \"{filename2}\"){spacestr1}={spacestr2}{state}"
    r = parse(format, line)
    if (r == None):
        return None, None, "FAIL"
    return r['filename1'], r['filename2'], str(r['timestamp'])


def get_CmdInfo(lines):
    lineNums = []
    fileList = []
    for line in lines:
        if ("to execute" in line and "line" in line):
            index1 = line.rfind(" ")
            index2 = line.rfind(")")
            strLineNum = line[(index1 + 1):index2]

            if ("`" in line):
                index3 = line.rfind("'")
                index4 = line.rfind("`")
            else:
                index3 = line.rfind("'")
                index4 = line.rfind("'", 0, index3)
            fileName = line[(index4 + 1):index3]

            if (int(strLineNum) in lineNums):
                index = lineNums.index(int(strLineNum))
                if (fileName == fileList[index]):
                    continue
            
            lineNums.append(int(strLineNum))
            fileList.append(fileName)
    return fileList, lineNums


def get_profile_targetLineNumber(filepath, CDG):
    profileLineNum = {}
    try:
        filep = open(filepath + "/profile.txt")
        lineNumber = 0
        while True:
            line = filep.readline()
            if not line:
                break
            lineNumber +=1 
            if ((not "#" in line) and (":" in line)):
                index = line.index(":")
                if (line[:index] in CDG.keys()):
                    profileLineNum[line[:index]] = lineNumber
    except Exception as es:
        print("Could not load %s" % (filepath))
        pass
    return profileLineNum


def get_DG_targetLineNum(outputpath):
    CDGLineNumber = {}
    DDGLineNumber = {}
    file1 = open(outputpath + "/originCDG.json")
    lineNumber = 1
    while True:
        line = file1.readline()
        if not line:
            break
        lineNumber += 1
        if (":" in line and "[" in line):
            index1 = line.rfind("\"")
            index2 = line.rfind("\"", 0, index1)
            target = line[(index2 + 1): index1]
            CDGLineNumber[target] = lineNumber
    
    file2 = open(outputpath + "/originDDG.json")
    lineNumber = 1
    while True:
        line = file2.readline()
        if not line:
            break
        lineNumber += 1
        if (not "\"" in line):
            continue
        if (line.index("\"") == 4):
            index3 = line.rfind("\"")
            index4 = line.rfind("\"", 0, index3)
            target = line[(index4 + 1): index3]
            DDGLineNumber[target] = lineNumber

    shortCDGLineNumber = {}
    shortDDGLineNumber = {}
    file3 = open(outputpath + "/shortCDG.json")
    lineNumber = 1
    while True:
        line = file3.readline()
        if not line:
            break
        lineNumber += 1
        if (":" in line and "[" in line):
            index1 = line.rfind("\"")
            index2 = line.rfind("\"", 0, index1)
            target = line[(index2 + 1): index1]
            shortCDGLineNumber[target] = lineNumber
    
    file4 = open(outputpath + "/shortDDG.json")
    lineNumber = 1
    while True:
        line = file4.readline()
        if not line:
            break
        lineNumber += 1
        if (not "\"" in line):
            continue
        if (line.index("\"") == 4):
            index3 = line.rfind("\"")
            index4 = line.rfind("\"", 0, index3)
            target = line[(index4 + 1): index3]
            shortDDGLineNumber[target] = lineNumber
    
    return CDGLineNumber, DDGLineNumber, shortCDGLineNumber, shortDDGLineNumber


def get_targetTrace(filepath):
    tracefile_path = os.path.normpath(filepath + "/trace.gdf.xml")
    DOMTree = libparse(tracefile_path)
    target_collection = DOMTree.documentElement
    targets = target_collection.getElementsByTagName("target")
 
    for target in targets:
        cmd_list = target.getElementsByTagName("command")
        actualcmd_list = target.getElementsByTagName("actual_command")
        for cmd in cmd_list:
            cmd_content = cmd.childNodes[0].data
        for actualcmd  in actualcmd_list:
            actualcmd_content = actualcmd.childNodes[0].data
    return


def iter_files(rootDir):
    filelist = []
    for root,dirs,files in os.walk(rootDir):
        for f in files:
            filename = os.path.join(root, f)
            filelist.append(filename)
        for dir in dirs:
            dirname = os.path.join(root, dir)
            filelist.extend(iter_files(dirname))
    return filelist


def clean(method, filepath):
    path = os.getcwd()
    os.chdir(filepath)
    if (method == "-configure"):
        os.system("./configure")
    if (method == "-config"):
        os.system("./config")
    # "x86-thing"
    # os.system("git clean -dxf -e profile.txt -e straceprofile\* -e makedebug")
    os.system("make clean")
    os.chdir(path)
    return