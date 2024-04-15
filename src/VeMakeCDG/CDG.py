import io
import re
from subprocess import check_call
import sys
import logging as log
import subprocess
import os
import copy
from VeMakeCDG.preprocess import *
import networkx as nx
from Util.parser import *
import json


def parse_makefile_aliases(profile_lines, filepath):
    cmd = ''
    target = ''
    is_target = True
    target2code_map = {}
    target2dir_map = {}
    dependency_tree = {}
    target_dir = filepath

    for line in profile_lines:
        if ("CURDIR" in line):
            tokens = re.split(':|=| ', line)
            tokens = list(filter(lambda x: x != '', tokens))
            target_dir = tokens[1].replace('\n','')
            continue
        if ('#' in line):
            if ('Not a target' in line):
                is_target = False
                continue
            else:
                cmd = line.lstrip('\t').rstrip('\n').lstrip('#').lstrip(' ').rstrip(' ')
                if (not target in target2code_map.keys()):
                    target2code_map[target] = []
                target2code_map[target].append(cmd)
        elif (':' in line and not line.startswith('\t') and not line.startswith(' ')):
            if (not is_target):
                is_target = True
            target = line.split(':')[0]
            target2dir_map[target] = target_dir
            if (not target in dependency_tree.keys()):
                dependency_tree[target] = []
            dependency_tree[target].extend(list(map(lambda s : s.rstrip('\n'), 
                                    list(filter(lambda c : c != '' and c != ' ', line.split(':')[1].split(' '))))))
            while ('' in dependency_tree[target]):
                dependency_tree[target].remove('')
            dependency_tree[target] = list(set(dependency_tree[target]))
            
    return dependency_tree, target2code_map, target2dir_map


def get_target_sequence(dependency_tree):
    all_target_sequence = []
    target_list = list(dependency_tree.keys())
    while len(target_list) > 0:
        prelength = len(target_list)
        tmp_target_list = []
        for target in target_list:
            tmp_target_list.append(target)
        for target in tmp_target_list:
            if set(dependency_tree[target]).issubset(set(all_target_sequence)):
                all_target_sequence.append(target)
                target_list.remove(target)
        succlength = len(target_list)
        if succlength == prelength:
            all_target_sequence.extend(target_list)
            break

    target_sequence = []
    for target in all_target_sequence:
        if dependency_tree[target] != []:
            target_sequence.append(target)          
    return target_sequence


def get_fileIndexMap(dependency_tree, target2dir_map, target_sequence):
    fileIndexMap = {}
    for notarget in dependency_tree.keys():
        if (not notarget in target_sequence):
            fileIndexMap[notarget] = my_normpath(target2dir_map[notarget], notarget)
    return fileIndexMap


def get_CDG(filepath, cleanmethod, jnum):
    """ Test execution """
    profile_lines = query_profile(filepath, cleanmethod, jnum)
    print("profile generation finished")
    dependency_tree, target2code_map, target2dir_map = parse_makefile_aliases(profile_lines, filepath)
    print("profile parse finished")
    target_sequence = get_target_sequence(dependency_tree)
    print("target seq obtained")
    fileIndexMap = get_fileIndexMap(dependency_tree, target2dir_map, target_sequence)
    print("file index map obtained")
    return dependency_tree, target_sequence, target2code_map, target2dir_map, fileIndexMap