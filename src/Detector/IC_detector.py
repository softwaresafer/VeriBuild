import io
import sys
import os
import json
import time
from VeMakeDDG.DDG import *
from Util.parser import *
from Util.operation import *


def IC_detecor(filepath, outputpath, cleanmethod, jnum):
    time_start = time.time()
    IO_compare_graph = {}
    make_inputfiles, make_outputfiles, make_createfiles, make_deletefiles = get_make_IOinfo(filepath, cleanmethod, jnum)
    clean_inputfiles, clean_outputfiles, clean_createfiles, clean_deletefiles = get_clean_IOinfo(filepath, cleanmethod, jnum)
    for subdeletefile in make_deletefiles.keys():
        if (subdeletefile in make_createfiles.keys()):
            if (make_deletefiles[subdeletefile] > make_createfiles[subdeletefile]):
                make_createfiles.pop(subdeletefile)
    for subcreatefile in clean_createfiles.keys():
        if (subcreatefile in clean_deletefiles.keys()):
            if (clean_deletefiles[subcreatefile] < clean_createfiles[subcreatefile]):
                clean_deletefiles.pop(subcreatefile)
    make_createfiles_set = set(make_createfiles.keys())
    clean_deletefiles_set = set(clean_deletefiles.keys())
    created_files_set = make_createfiles_set.difference(clean_deletefiles_set)
    deleted_files_set = clean_deletefiles_set.difference(make_createfiles_set)
    IO_compare_graph["created_files"] = list(created_files_set)
    IO_compare_graph["deleted_files"] = list(deleted_files_set)
    time_end = time.time()
    file8 = open(outputpath + '/IC.json', 'w')
    json.dump(IO_compare_graph, file8, indent=4)
    return (time_end - time_start), IO_compare_graph

    