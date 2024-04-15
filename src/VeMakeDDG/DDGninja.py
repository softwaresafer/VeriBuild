from Util.parser import *

# Created by Chasen Wang on Dec 30, 2019

#############################################
# Developer's Notes:
# 1. strace command might be incorrect(get_ninja_target_IO)
# 2. The format of Ninja stracefiles might be different from the ones of GNU Make(parse_ninja_target_IO)
# 3. The phase of merge IO information is error prone(get_DDG_ninja)
#############################################


def file_filter(filename):
    if filename.endswith(".ninja_log") or filename.endswith(".ninja_deps"):
        return True
    if filename.endswith("rules.ninja") or filename.endswith("build.ninja"):
        return True
    if filename.endswith("/sys/devices/system/cpu/online"):
        return True
    return False


def filedic_filter(filedic):
    new_filedic = {}
    for filename in filedic.keys():
        if not file_filter(filename):
            new_filedic[filename] = filedic[filename]
    return new_filedic


def get_DDG_ninja(filepath, CDG, target_sequence, jnum):
    # Step 1: get the IO information
    # building each targets in the sequence subjecting to static dependency relation
    tmp_DDG = {}
    for target in target_sequence:
        tmp_inputfiles, tmp_outputfiles, tmp_createfiles, tmp_deletefiles = get_ninja_target_IO(filepath, target, jnum)
        if target not in tmp_DDG.keys():    # can be omitted
            tmp_DDG[target] = {}
            tmp_DDG[target]["input"] = filedic_filter(tmp_inputfiles)
            tmp_DDG[target]["output"] = filedic_filter(tmp_outputfiles)
            tmp_DDG[target]["create"] = filedic_filter(tmp_createfiles)
            tmp_DDG[target]["delete"] = filedic_filter(tmp_deletefiles)


    # Step 2: merge the IO information and get DDG
    DDG = {}
    DDG = tmp_DDG
    # for target in target_sequence:
    #     prerequsites = CDG[target]
    #     DDG[target] = {}
    #     DDG[target]["input"] = {}
    #     DDG[target]["output"] = {}
    #     DDG[target]["create"] = {}
    #     DDG[target]["delete"] = {}
    #     # the IO info of its prerequisites
    #     for prerequsite in prerequsites:
    #         # TODO: ERROR PRONE
    #         # Description: timestamp and the order of build might cause error when generating DDG for Ninja system
    #         DDG[target]["input"].update(tmp_DDG[prerequsite]["input"])
    #         DDG[target]["output"].update(tmp_DDG[prerequsite]["output"])
    #         DDG[target]["create"].update(tmp_DDG[prerequsite]["create"])
    #         DDG[target]["delete"].update(tmp_DDG[prerequsite]["delete"])
    #     # the IO info of its own
    #     DDG[target]["input"].update(tmp_DDG[target]["input"])
    #     DDG[target]["output"].update(tmp_DDG[target]["output"])
    #     DDG[target]["create"].update(tmp_DDG[target]["create"])
    #     DDG[target]["delete"].update(tmp_DDG[target]["delete"])

    # Step 3: clean the targets
    path = os.getcwd()
    newpath = filepath
    os.chdir(newpath)
    os.system("ninja clean")
    os.chdir(path)
    return DDG


def get_ninja_target_IO(filepath, target, jnum):
    # build the target
    path = os.getcwd()
    newpath = filepath
    os.chdir(newpath)
    # TODO: ERROR PRONE
    # debug info
    print("building target: " + target)
    os.system("strace -s 65535 -tt -f -o straceprofile -e trace=open,close,read,write,getcwd,unlink,execve ninja " + target + " -j " + str(jnum))
    filename = os.getcwd() + "/straceprofile"
    lines = []
    for line in open(filename):
        lines.append(line)
    os.remove(filename)
    os.chdir(path)
    print(len(lines))
    # parse the stracefile and get io information
    inputfiles, outputfiles, createfiles, deletefiles = parse_ninja_target_IO(filepath, lines)
    return inputfiles, outputfiles, createfiles, deletefiles


def parse_ninja_target_IO(filepath, profile_content):
    inputfiles = {}
    outputfiles = {}
    createfiles = {}
    deletefiles = {}
    # TODO: ERROR PRONE
    # Description: Ninja has different features from the ones in GNU make, for example *current path* and *target name*
    curdir = filepath
    isinit = False
    for line in profile_content:
        #print(line)
        if ' ' not in line:
            continue
        postline = line[line.find(" ") + 1:]
        # if postline.startswith("chdir"):
        if "chdir" in postline:
            tmpcurdir = get_cwd(postline)
            if tmpcurdir != None:
                curdir = my_normpath(curdir, tmpcurdir)
            continue
        # if postline.startswith("unlink"):
        if "unlink" in postline:
            filename, timestamp = get_unlinkedfile(postline)
            if (filename != None and timestamp != None):
                deletefiles[my_normpath(curdir, filename)] = timestamp
            continue
        # if postline.startswith("execve"):
        if "execve" in postline:
            if not isinit:
                tmpcurdir = get_initpwd(postline)
                if tmpcurdir != None:
                    curdir = tmpcurdir
                    isinit = True
                    continue
            filename, timestamp, mode = get_execvefile(postline)
            if "SUCCESS" in mode:
                inputfiles[my_normpath(curdir, filename)] = timestamp
            continue
        # if postline.startswith("open"):
        if "open" in postline:
            filename, timestamp, mode = get_openedfile(postline)
            if "O_RDONLY" in mode:
                inputfiles[my_normpath(curdir, filename)] = timestamp
            elif "O_WRONLY" in mode or "O_RDWR" in mode:
                outputfiles[my_normpath(curdir, filename)] = timestamp
            elif "O_CREAT" in mode:
                outputfiles[my_normpath(curdir, filename)] = timestamp
                createfiles[my_normpath(curdir, filename)] = timestamp
            elif "FAIL" in mode:
                continue
        # if postline.startswith("rename"):
        if "rename" in postline:
            filename1, filename2, timestamp = get_renamedfile(postline)
            if timestamp != "FAIL":
                createfiles[my_normpath(curdir, filename2)] = timestamp
                deletefiles[my_normpath(curdir, filename1)] = timestamp
                outputfiles[my_normpath(curdir, filename2)] = timestamp
                continue
    return inputfiles, outputfiles, createfiles, deletefiles
