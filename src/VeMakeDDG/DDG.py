import io
import sys
import os
import copy
import re
from VeMakeDDG.preprocess import *
from Util.parser import *


def get_pid_tree(filepath, target, cleanmethod, jnum):
    pid_tree = {}
    pidlist, profile_contents, pidtarget_map = query_profile(filepath, target, cleanmethod, jnum)
    for pid in pidlist:
        pid_tree[pid] = get_sub_pidlist(profile_contents[pid])

    pidtarget_list = list(pidtarget_map.keys())
    for pid in pidtarget_list:
        subpidlist = get_sub_pidtable([], pid, pid_tree)
        for subpid in subpidlist:
            pidtarget_map[subpid] = pidtarget_map[pid]
    return pid_tree, pidlist, profile_contents, pidtarget_map

    
def get_sub_pidtable(subpidlist, pid, pid_tree):
    pidls = pid_tree[pid]
    new_subpidlist = []
    for subpid in pidls:
        new_subpidlist.append(subpid)
        new_subpidlist.extend(get_sub_pidtable([], subpid, pid_tree))
    new_subpidlist.append(pid)
    return new_subpidlist


def get_sub_pidlist(profile_content):
    sub_pidlist = []
    for line in profile_content:
        if (not "--- SIGCHLD" in line):
            continue
        index = line.find("si_pid=")
        newline = line[(index + 7):]
        sub_pidlist.append(newline[:newline.find(",")])
    return sub_pidlist

def get_process_IOinfo(filepath, pid, profile_content):
    inputfiles = {}
    outputfiles = {}
    createfiles = {}
    deletefiles = {}
    # TODO
    curdir = filepath
    isinit = False
    for line in profile_content:
        line = line.rstrip()
        postline = line.split(' ')[1]
        if (postline.startswith("chdir")):
            tmpcurdir = get_cwd(line)
            if (tmpcurdir != None):
                curdir = my_normpath(curdir, tmpcurdir)
            continue
        if (postline.startswith("unlink")):
            filename, timestamp = get_unlinkedfile(line)
            if (filename != None and timestamp != None):
                deletefiles[my_normpath(curdir, filename)] = timestamp
            continue
        if (postline.startswith("execve")):
            if (not isinit):
                tmpcurdir = get_initpwd(line)
                if (tmpcurdir != None):
                    curdir = tmpcurdir
                    isinit = True
                    continue
            filename, timestamp, mode = get_execvefile(line)
            if ("SUCCESS" in mode):
                inputfiles[my_normpath(curdir, filename)] = timestamp
            continue
        if (postline.startswith("openat")):
            filename, timestamp, mode = get_openedfile(line)
            if ("O_RDONLY" in mode):
                inputfiles[my_normpath(curdir, filename)] = timestamp
            elif ("O_WRONLY" in mode or "O_RDWR" in mode):
                outputfiles[my_normpath(curdir, filename)] = timestamp
            elif ("O_CREAT" in mode):
                outputfiles[my_normpath(curdir, filename)] = timestamp
                createfiles[my_normpath(curdir, filename)] = timestamp
            elif ("FAIL" in mode):
                continue
        if (postline.startswith("rename")):
            filename1, filename2, timestamp = get_renamedfile(line)
            createfiles[my_normpath(curdir, filename2)] = timestamp
            deletefiles[my_normpath(curdir, filename1)] = timestamp
            outputfiles[my_normpath(curdir, filename2)] = timestamp
            continue
    return inputfiles, outputfiles, createfiles, deletefiles


def get_make_IOinfo(filepath, cleanmethod, jnum):
    path = os.getcwd()
    newpath = filepath
    os.chdir(newpath)
    os.system("strace -s 65535 -tt -f -o straceprofile -e trace=open,close,read,write,getcwd,unlink,execve make -j " + str(jnum))
    filename = os.getcwd() + "/straceprofile"
    lines = []
    for line in open(filename):
        lines.append(line)
    os.remove(filename)
    os.chdir(path)
    return get_process_IOinfo(filepath, None, lines)


def get_clean_IOinfo(filepath, cleanmethod, jnum):
    path = os.getcwd()
    newpath = filepath
    os.chdir(newpath)
    os.system("strace -s 65535 -tt -f -o straceprofile -e trace=open,close,read,write,getcwd,unlink,execve make clean -j " + str(jnum))
    filename = os.getcwd() + "/straceprofile"
    lines = []
    for line in open(filename):
        lines.append(line)
    os.remove(filename)
    clean(cleanmethod, filepath)
    os.chdir(path)
    return get_process_IOinfo(filepath, None, lines)


def get_target_IOinfo(pid, pid_tree, tmpDDG):
    inputfiles = {}
    outputfiles = {}
    createfiles = {}
    deletefiles = {}
    if (pid_tree[pid] == []):
        inputfiles = tmpDDG[pid]["input"]
        outputfiles = tmpDDG[pid]["output"]
        createfiles = tmpDDG[pid]["create"]
        deletefiles = tmpDDG[pid]["delete"]
    else:
        for subpid in pid_tree[pid]:
            sub_inputfiles, sub_outputfiles, sub_createfiles, sub_deletefiles = get_target_IOinfo(subpid, pid_tree, tmpDDG)
            inputfiles.update(sub_inputfiles)
            outputfiles.update(sub_outputfiles)
            createfiles.update(sub_createfiles)
            deletefiles.update(sub_deletefiles)
    return inputfiles, outputfiles, createfiles, deletefiles


def get_DDG(filepath, toptargets, cleanmethod, jnum):
    olddir = os.getcwd()
    tmpDDG = {}
    DDG = {}
    t_pidtarget_map = {}
    for toptarget in toptargets:
        if (toptarget == "all-am"):
            continue
        print("make target " + toptarget)
        pid_tree, pidlist, profile_contents, pidtarget_map = get_pid_tree(filepath, toptarget, cleanmethod, jnum)
        t_pidtarget_map.update(pidtarget_map)
        for pid in pidlist:
            inputfiles, outputfiles, createfiles, deletefiles = get_process_IOinfo(filepath, pid, profile_contents[pid])
            tmpDDG[pid] = {}
            tmpDDG[pid]["input"] = inputfiles
            tmpDDG[pid]["output"] = outputfiles
            tmpDDG[pid]["create"] = createfiles
            tmpDDG[pid]["delete"] = deletefiles
        for pid in pidtarget_map.keys():
            inputfiles, outputfiles, createfiles, deletefiles = get_target_IOinfo(pid, pid_tree, tmpDDG)
            if (pidtarget_map[pid] in DDG.keys()):
                DDG[pidtarget_map[pid]]["input"].update(inputfiles)
                DDG[pidtarget_map[pid]]["output"].update(outputfiles)
                DDG[pidtarget_map[pid]]["create"].update(createfiles)
                DDG[pidtarget_map[pid]]["delete"].update(deletefiles)
            else:
                DDG[pidtarget_map[pid]] = {}
                DDG[pidtarget_map[pid]]["input"] = inputfiles
                DDG[pidtarget_map[pid]]["output"] = outputfiles
                DDG[pidtarget_map[pid]]["create"] = createfiles
                DDG[pidtarget_map[pid]]["delete"] = deletefiles
    os.chdir(olddir)
    clean(cleanmethod, filepath)
    return DDG, t_pidtarget_map
