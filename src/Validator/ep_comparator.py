#!/usr/bin/env python3

import argparse
import json
import parse
import sys
from collections import defaultdict
import networkx
import os
# argvs
# initiate the parser
parser = argparse.ArgumentParser()
# add long and short argument
parser.add_argument("--mc-report", "-m", dest='mcreport', type=str, help="set the path of mcreport")
parser.add_argument("--vb-report", "-v", dest='vbreport', type=str, help="set the path of Veribuild report")
parser.add_argument("--vb-sdg ", "-s", dest='sdg', type=str, help="set the path of Veribuild Static Dependency Graph")
parser.add_argument("--output ", "-o", dest='outputpath', type=str, help="set output path")

args = parser.parse_args()


def filepath_to_json(filepath:str):
    with open(filepath, "r") as f:
        return json.load(fp=f)

    return None

def load_mc_report(report_path:str):
    
    target_line_parser = parse.compile("[{index:d}/{total:d}] {filepath}:")
    issue_line_parser = parse.compile("  {op} {filepath} ({process})")

    # The default value for any key is an empty list.
    EPs = defaultdict(lambda: [])
    EPs_of_mv = defaultdict(lambda: [])  # mv may result in FPs in mkcheck
    MPs = defaultdict(lambda: [])
    
    with open(report_path, "r") as f:
        file_to = None
        for line_num, line in enumerate(f.readlines()):
            if line.startswith("["): 
                # [4/573] /home/nand/Vemake/testbase/testproject/gmp/compat.c:
                # + /home/nand/Vemake/testbase/testproject/gmp/compat.lo (mv)
                r = target_line_parser.parse(line)
                file_to = r["filepath"]
            elif line.startswith("  "):
                r = issue_line_parser.parse(line)
                if r["op"] is '+':
                    # EP
                    if r["process"] == "mv":
                        EPs_of_mv[r["filepath"]].append(file_to)
                    else:
                        EPs[r["filepath"]].append(file_to)
                elif r["op"] is '-':
                    # MP
                    MPs[r["filepath"]].append(file_to)
                else:
                    print >> sys.stderr, "Operator not supported."
                    sys.exit(1)
    print("EPs: {}".format(EPs))
    #print("MPs: {}".format(MPs))    
    return MPs, EPs, EPs_of_mv

def convert_fullpathdict_to_basenamedict(d:dict):
    """
        convert a dict with full paths to a dict with basenames.
    """ 
    base_dict = dict()
    for k, v in d.items():
        base_dict[os.path.basename(k)]  = [os.path.basename(f) for f in v]
    return base_dict


def dep_dict_to_edges(d:dict):
    l = []
    for k,v in d.items():
        l.extend([(k,i) for i in v])
    return set(l)

def edges_to_dep_dict(l:list):
    d = defaultdict(lambda: [])
    for k,v in l: 
        d[k].append(v)

    return d


def main():
    MC_MPs, MC_EPs, EPs_of_mv = load_mc_report(args.mcreport)
    vbreport = filepath_to_json(args.vbreport)
    vbsdg = filepath_to_json(args.sdg)

    # basename level SDG
    # For simplicity we map all filepaths to filenames. e.g., /usr/bin/a.c --> a.c
    SDG = networkx.DiGraph()
    for key in vbsdg.keys():
        SDG.add_edges_from([(os.path.basename(key),os.path.basename(v)) for v in vbsdg[key]])
    
    # basename level MC Reports. 
    MC_EPs_base = dict()
    print("hello")
    print(MC_EPs)
    for k, v in MC_EPs.items():
        MC_EPs_base[os.path.basename(k)]  = [os.path.basename(f) for f in v]

    # basename level VB Reports. 
    vbreport_base = dict()
    for k, v in vbreport.items():
        vbreport_base[os.path.basename(k)]  = [os.path.basename(f) for f in v["Excessive Prerequisites"]]


    # Convert them to sets of edges.
    mc_ep_set = dep_dict_to_edges(MC_EPs_base)
    vb_ep_set = dep_dict_to_edges(vbreport_base)
    
    # Output Statistics.
    results = {}
    results["n_mc_org"] = len(mc_ep_set)
    results["n_mc_of_mv"] = len(EPs_of_mv)

    # A set with all non-makefile edges filtered.
    mc_ep_set_with_non_make_edges = set([(s,t) for s,t in mc_ep_set if SDG.has_node(s) and SDG.has_node(t)])
    results["n_mc_mfile"] = len(mc_ep_set_with_non_make_edges)

    # Ignore Config Edges. 
    config_files = ["config.h", "settings.h", "config.h.in"]
    mc_config_ep = set(filter(lambda t: t[1] in config_files, mc_ep_set_with_non_make_edges))
    results["n_mc_conf"] = len(mc_config_ep)
    mc_ep_set_with_non_make_edges = mc_ep_set_with_non_make_edges - mc_config_ep

    vb_config_ep = set(filter(lambda t: t[1] in config_files, vb_ep_set))
    results["n_vb_conf"] = len(vb_config_ep)
    vb_ep_set = vb_ep_set - vb_config_ep

    # Edegs with distance=1 is comparable with Veribuild.
    sp = dict(networkx.all_pairs_shortest_path_length(SDG))
    mc_ep_immediate_edges = set([(s,t) for s,t in mc_ep_set_with_non_make_edges if (t in sp[s]) and sp[s][t] == 1])


    # Compare the two
    # a helper function for recording edges.
    def record_edges_to_dict(l:list, type:str, results:dict):
        results["n_"+type] = len(l)
        results["edges_"+type] = edges_to_dep_dict(l)

    # Same EPs edges. 
    record_edges_to_dict(mc_ep_immediate_edges & vb_ep_set, "allhave", results)
    # MC unique edges
    record_edges_to_dict(mc_ep_immediate_edges - vb_ep_set, "mc_unique", results)
    # VB unique edges
    record_edges_to_dict(vb_ep_set - mc_ep_immediate_edges, "vb_unique", results)

    results["n_mc_edges"] = len(mc_ep_immediate_edges)
    results["n_vb_edges"] = len(vb_ep_set)

    # Remove the edges in case the dependency relation are two far.
    # sp = dict(networkx.all_pairs_shortest_path_length(SDG))
    # for s,t in mc_ep_set:
    #     print("{}->{}: distance: {}".format(s,t,sp[s][t]))


    print(results)

    with open(args.outputpath, "w") as f: 
        json.dump(results, fp=f, indent=4)


if __name__ == '__main__':
    exit(main())