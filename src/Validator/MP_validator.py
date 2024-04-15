import io
import sys
import os
import json
import time
from Util.parser import *
from Util.operation import *

def MP_validator(filepath, cleanmethod, MP_result):
    MP_Truebugs = {}
    os.chdir(filepath)
    if (cleanmethod == "-configure"):
        os.system("./configure")
    
    for target in MP_result.keys():
        print("validate " + target)
        if (target == "depend" or target == "_all" or target == "all"):
            continue
        os.system("make " + target + " -j 40")
        for prefile in MP_result[target]["Missing Prerequisites"]:
            print("validate " + target)
            os.system("touch " + prefile)
            r = os.popen("make " + target + " -j 40")
            info = r.readlines()
            if (len(info) > 0):
                if ("up to date" in info[-1]):
                    if (not target in MP_Truebugs.keys()):
                        MP_Truebugs[target] = []
                    MP_Truebugs[target].append(prefile)
    return MP_Truebugs
