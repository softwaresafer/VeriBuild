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

if __name__ == "__main__":
    statistical_res = {}
    files = os.listdir("/home/vemakecreator/Vemake/testbase/compare")
    for f in files:
        filex = open("/home/vemakecreator/Vemake/testbase/compare/" + f, 'r+')
        compare_result = eval(filex.read())
        EP_compare_data = compare_result["EP(mkcheck own | vemake own | shared)"]
        MP_compare_data = compare_result["MP(mkcheck own | vemake own | shared)"]
        print(str(MP_compare_data) + "       " + str(EP_compare_data) + "       " + f)
        statistical_res[f] = {}
        statistical_res[f]["MP"] = str(MP_compare_data)
        statistical_res[f]["EP"] = str(EP_compare_data)

    resfile = open("/home/vemakecreator/Vemake/testbase/compare_statistics.json", 'w')
    json.dump(statistical_res, resfile, indent=4)


    