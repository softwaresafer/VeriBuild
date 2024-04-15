#!/usr/bin/env python3
'''
This is the script used for Jenkins Job: vemake_run_ep_mp_for_one_project
It has two environments variables : PROJECTS, RULES
PROJECTS is a string array such as: Bftpd;bftpd;bftpd,Bftpd;bftpd;bftpd
RULES is a string array such as: EP,MP

'''

import os
import subprocess

def get_projects():
    projects = []

    for one_entry in os.environ['PROJECTS'].split(','):
        name, builddir, srcdir = one_entry.split(';')
        project_descripor = dict(name=name, builddir=builddir, srcdir=srcdir) 
        projects.append(project_descripor)

    print("{}".format(projects))
    return projects

def get_rules():
    return os.environ['RULES'].split(',')


def run_for_single_project(project_dict, rules):
    
    vemake_root = "/home/vemakecreator/CODEBASE/veribuild/Vemake/VemakeTool/vemake/tool/src"
    builddir = os.path.join(os.path.expanduser("~"),"Vemake", "testbase", "testproject", project_dict["builddir"])
    
    cmds = [vemake_root+"/run.py", "-cache", "-f", builddir]
    cmds.extend(["-"+t for t in rules])
    print("Execute Cmds: {}".format(" ".join(cmds)))

    ret = subprocess.call(cmds, shell=False, cwd = vemake_root)
    print("Execution Result: ret = {}".format(ret))

projects = get_projects()
rules = get_rules()
print("Projects {}".format(projects))
print("Rules {}".format(rules))

for project in projects:
    run_for_single_project(project, rules)