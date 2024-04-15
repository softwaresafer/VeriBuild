import networkx as nx
from Util.parser import *
from copy import deepcopy

# Created by Chasen Wang on Dec 27, 2019

# def is_in_blacklist(target_name):
#     if target_name.endswith("ninja") or target_name.endswith("cmake") or target_name.endswith("util"):
#         return True
#     return False


def get_whitespace_num(s):
    num = 0
    while s[num] == " ":
        num += 1
    return num


def get_target_sequence(dependency_tree):
    # topological sort
    dep_tree_graph = deepcopy(dependency_tree)
    G = nx.DiGraph()
    edges_list = [((nbr, node)) for node, nbrlist in dep_tree_graph.items() for nbr in nbrlist]
    G.add_edges_from(edges_list)
    target_sequence = nx.topological_sort(G)
    # debug info
    print("target sequence")
    print(target_sequence)
    return target_sequence


def get_CDG_ninja(filepath):
    path = os.getcwd()
    os.chdir(filepath)
    r = os.popen("ninja -t targets depth 0")
    info = r.readlines()
    os.chdir(path)

    dependency_tree = {}
    file_index_map = {}
    target_tmp_list = []
    indent = -2

    for line in info:
        new_indent = get_whitespace_num(line)
        target_name = line[:line.find(":")].lstrip(" ")
        # if is_in_blacklist(target_name):
        #     continue
        if ":" not in line:
            target_name = my_normpath(filepath, target_name)
            file_index_map[target_name] = target_name
        if new_indent > indent:
            if indent > -2:
                last_target = target_tmp_list[-1]
                dependency_tree[last_target].append(target_name)
            indent += 2
        elif new_indent == indent:
            if indent == 0:
                target_tmp_list = []
            else:
                target_tmp_list.pop()
                last_target = target_tmp_list[-1]
                dependency_tree[last_target].append(target_name)
        else:
            while new_indent < indent:
                target_tmp_list.pop()
                indent -= 2
            target_tmp_list.pop()
            indent = new_indent
            if len(target_tmp_list) > 0:
                last_target = target_tmp_list[-1]
                dependency_tree[last_target].append(target_name)

        target_tmp_list.append(target_name)
        if target_name not in dependency_tree.keys():
            dependency_tree[target_name] = []

    for target in dependency_tree.keys():
        dependency_tree[target] = list(set(dependency_tree[target]))

    new_dependenency_tree = {}
    for target in dependency_tree.keys():
        new_dependenency_tree[target] = []
        for prerequisite in dependency_tree[target]:
            if prerequisite in file_index_map.keys():
                new_dependenency_tree[target].append(file_index_map[prerequisite])
            else:
                new_dependenency_tree[target].append(prerequisite)
    target_sequence = get_target_sequence(dependency_tree)
    print("ninja CDG obtained")
    return new_dependenency_tree, target_sequence, file_index_map
