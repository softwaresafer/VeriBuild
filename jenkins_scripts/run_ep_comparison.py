#!/usr/bin/env python3
'''
This is the script used for Jenkins Job: vemake_run_ep_comparison
It has two environments variables : PROJECTS, RULES
PROJECTS is a string array such as: Bftpd;bftpd;bftpd,Bftpd;bftpd;bftpd
RULES is a string array such as: EP,MP

'''

import os
import subprocess
import json

def get_projects():
    projects = []

    for one_entry in os.environ['PROJECTS'].split(','):
        name, builddir, srcdir = one_entry.split(';')
        project_descripor = dict(name=name, builddir=builddir, srcdir=srcdir) 
        projects.append(project_descripor)

    print("{}".format(projects))
    return projects

def get_rules():
    if 'RULES' in os.environ:
        return os.environ['RULES'].split(',')
    return []
    
def get_workspace():
    return os.environ['WORKSPACE']

def run_for_single_project(project_dict, rules):
    
    vemake_root = "/home/vemakecreator/CODEBASE/veribuild/Vemake/VemakeTool/vemake/tool/src"
    builddir = os.path.join(os.path.expanduser("~"),"Vemake", "testbase", "testproject", project_dict["builddir"])
    
    workspace_root = "/home/vemakecreator/CODEBASE/veribuild/Vemake/testbase/testoutput/{}".format(project_dict["builddir"])

    # Very bad due to inconsistant file names.
    guess_name = os.path.basename(project_dict["name"]).replace(" ", "_")
    mc_report_path = "/home/nand/Vemake/buildfuzz_results/mkcheck_fuzz_stdout_{}.txt".format(guess_name)
    vb_ep_path = os.path.join(workspace_root, "EP.json")
    sdg_path = os.path.join(workspace_root, "originCDG.json")
    output_path = os.path.join(os.getcwd(), guess_name+".json")

    cmds = [vemake_root+"/Validator/ep_comparator.py", "--mc-report", mc_report_path, 
        "--vb-report", vb_ep_path,
        "--vb-sdg", sdg_path,
        "-o", output_path]

    print("Execute Cmds: {}".format(" ".join(cmds)))

    ret = subprocess.call(cmds, shell=False, cwd = vemake_root, stdout=open(os.devnull, 'wb'))
    print("Execution Result: ret = {}".format(ret))
    
    result = dict(status="Success" if ret else "Failed")
    if ret == 0:
        # Append more information.
        with open(output_path, "r") as f:
            json_result = json.load(fp=f)
            return True, json_result

    return False, None

def print_results(results:dict):
    # hack, get keys from the first element. 
    items = []
    for project, v in results.items():
        items = sorted([k for k in v.keys() if k.startswith("n_")])
        break
    # convert dict to a table like dict.
    # items = ["Project", "mc_edges", "vb_edges", "allhave", "mc_unique", "vb_unique", "mc_org", "mc_mkf", "mc_ep_of_mv"]
    format_str = "{:>6}" + "{:>24}"+"{:>12}" * (len(items))

    # Print header
    print(format_str.format("", "Project", *items))

    index = 1
    for project,v in results.items():
        # project is the project name
        row = [index, project, *[v[k] for k in items]]
        print(format_str.format(*row))
        index = index + 1


projects = get_projects()
rules = get_rules()
print("Projects {}".format(projects))

results = dict()
for project in projects:
    suc, r = run_for_single_project(project, rules)
    if suc:
        results[project["name"]] = r
    else:
        print("\t{} Failed".format(project["name"]))
print_results(results)