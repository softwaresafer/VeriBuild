import io
import sys
import os
import re
from Util.parser import *


def query_profile_ninja(filepath, target, cleanmethod, jnum):
    path = os.getcwd()
    newpath = filepath
    os.chdir(newpath)
    prefiles = list(set(my_iter_files(os.getcwd())))
    generate_profile_ninja(filepath, target, cleanmethod, jnum)
    print("profile generation finished")
    pidlist = get_pidlist()
    print("pid list obtained")
    pidtarget_map = get_pidtarget_map()
    print("pidtarget map obtained")
    # os.system("make clean")
    clean(cleanmethod, filepath)
    postfiles = list(set(my_iter_files(os.getcwd())))

    profile_contents = {}
    for pid in pidlist:
        lines = get_singleprofile(pid)
        profile_contents[pid] = lines

    for f in postfiles:
        if (not f in prefiles):
            name, ext = os.path.splitext(f)
            if "straceprofile" in name:
                os.remove(f)
    os.chdir(path)
    return pidlist, profile_contents, pidtarget_map


def query_profile(filepath, target, cleanmethod, jnum):
    path = os.getcwd()
    newpath = filepath 
    os.chdir(newpath)
    prefiles = list(set(my_iter_files(os.getcwd())))
    generate_profile(filepath, target, cleanmethod, jnum)
    print("profile generation finished")
    pidlist = get_pidlist()
    print("pid list obtained")
    pidtarget_map = get_pidtarget_map()
    print("pidtarget map obtained")
    # os.system("make clean")
    clean(cleanmethod, filepath)
    postfiles = list(set(my_iter_files(os.getcwd())))
    
    profile_contents = {}
    for pid in pidlist:
        lines = get_singleprofile(pid)
        profile_contents[pid] = lines

    for f in postfiles:
        if (not f in prefiles):
            name, ext = os.path.splitext(f)
            if ("straceprofile" in name):
                os.remove(f)
    os.chdir(path)
    return pidlist, profile_contents, pidtarget_map


def my_iter_files(rootDir):
    filelist = []
    for root,dirs,files in os.walk(rootDir):
        for f in files:
            filename = os.path.join(root, f)
            filelist.append(filename)
        for dir in dirs:
            dirname = os.path.join(root, dir)
            filelist.extend(my_iter_files(dirname))
    return filelist


def generate_profile(filepath, target, cleanmethod, jnum):
    files = os.listdir(os.getcwd()) 
    for f in files:
        if os.path.basename(f).startswith('straceprofile'):
            os.remove(f)
    # os.system("strace -v -s 65535 -tt -ff -o straceprofile -e trace=open,close,read,write,getcwd,chdir,unlink,rename,execve make -B --debug=j " + target + " -j " + str(jnum) + " > makedebug")   
    # print("straceprofile generated")
    os.system("strace -v -s 65535 -tt -ff -y -o straceprofile -e trace=openat,close,read,write,getcwd,chdir,unlink,rename,execve make --debug=j " + target + " -j " + str(jnum) + " > makedebug")   
    print("straceprofile generated")


def generate_profile_ninja(filepath, target, cleanmethod, jnum):
    files = os.listdir(os.getcwd())
    for f in files:
        if os.path.basename(f).startswith('straceprofile'):
            os.remove(f)
    # os.system("strace -v -s 65535 -tt -ff -o straceprofile -e trace=open,close,read,write,getcwd,chdir,unlink,rename,execve make -B --debug=j " + target + " -j " + str(jnum) + " > makedebug")
    # print("straceprofile generated")
    os.system("strace -v -s 65535 -tt -ff -o straceprofile -e trace=open,close,read,write,getcwd,chdir,unlink,rename,execve ninja " + target + " -j " + str(jnum) + " > makedebug")
    print("straceprofile generated")


def get_pidlist():
    files = os.listdir(os.getcwd())
    pidlist = []
    for f in files:
        if os.path.basename(f).startswith('straceprofile'):
            pidstr = os.path.basename(f)[14:]
            pidlist.append(pidstr)
    pidlist.sort()
    return pidlist


def get_singleprofile(pid):
    filename = os.getcwd() + "/straceprofile." + pid
    lines = []
    for line in open(filename):
        lines.append(line)
    return lines


def get_pidtarget_map():
    filename = os.getcwd() + "/makedebug"
    pidtarget_map = {}
    for line in open(filename):
        if (("Putting child" in line or "Live child" in line) and "PID" in line):
            tokens = re.split('\(|\)| ', line)
            tokens = list(filter(lambda x: x != '', tokens))
            pidtarget_map[tokens[5]] = tokens[3]
    return pidtarget_map