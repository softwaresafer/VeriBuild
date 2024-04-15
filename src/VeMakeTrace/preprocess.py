import io
import sys
import os
import re
from Util.parser import * 

def query_trace(filepath, toptargets, cleanmethod, jnum):
    generate_trace(filepath, toptargets, cleanmethod, jnum)
    print("trace generation finished")
    clean(cleanmethod, filepath)
    return


def generate_trace(filepath, toptargets, cleanmethod, jnum):
    path = os.getcwd()
    newpath = filepath 
    clean(cleanmethod, filepath)
    os.chdir(newpath)
    os.system(path + "/../lib/makao/parsing/bin/makewrapper.sh -B 2 > trace.txt")
    os.system(path + "/../lib/makao/parsing/bin/generate_makao_graph.pl -in trace.txt -out trace.gdf -format gdf")
    get_targetTrace(filepath)

    # files = os.listdir(os.getcwd()) 
    # for f in files:
    #     if os.path.basename(f).startswith('trace'):
    #         os.remove(f)


    # for target in toptargets:
    #     clean(cleanmethod, filepath)
    #     print("make " + target)
    #     os.chdir(filepath)
    #     os.system(path + "/../lib/makao/parsing/bin/makewrapper.sh " + target + " 2 > trace.txt")
    #     os.system(path + "/../lib/makao/parsing/bin/generate_makao_graph.pl -in trace.txt -out trace.gdf -format gdf")

    #     # TODO: parse the trace.gdf
    #     get_targetTrace()

    #     files = os.listdir(os.getcwd()) 
    #     for f in files:
    #         if os.path.basename(f).startswith('trace'):
    #             os.remove(f)
    os.chdir(path)