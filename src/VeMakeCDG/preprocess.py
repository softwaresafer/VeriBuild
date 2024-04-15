import io
import sys
import os
from Util.parser import * 

def query_profile(filepath, cleanmethod, jnum):
    path = os.getcwd()
    prefiles = list(set(my_iter_files(os.getcwd())))
    generate_profile(filepath, cleanmethod, jnum)
    postfiles = list(set(my_iter_files(os.getcwd())))
    profile_lines = parse_profile("profile.txt")
    os.chdir(path)
    return profile_lines


def query_profile_ninja(filepath, cleanmethod, jnum):
    path = os.getcwd()
    prefiles = list(set(my_iter_files(os.getcwd())))
    generate_profile_ninja(filepath, cleanmethod, jnum)
    postfiles = list(set(my_iter_files(os.getcwd())))
    profile_lines = parse_profile_ninja("build.ninja")
    os.chdir(path)
    return profile_lines


def generate_profile(filepath, cleanmethod, jnum):
    os.chdir(filepath)
    # os.system("make -t -j " + str(jnum) + " -p > profile.txt")
    os.system("make -j 50 -p > profile.txt")
    clean(cleanmethod, filepath)

# MAY NOT BE USED
# NINJA -T DEPS IS NOT PRECISE
def generate_profile_ninja(filepath, cleanmethod, jnum):
    os.chdir(filepath)
    os.system("ninja -t deps > profile_ninja.txt")
    clean(cleanmethod, filepath)


def my_iter_files(rootDir):
    filelist = []
    for root,dirs,files in os.walk(rootDir):
        for f in files:
            filename = os.path.join(root, f)
            filelist.append(filename)
        for dir in dirs:
            dirname = os.path.join(root, dir)
            filelist.extend(my_iter_files(dirname))
    return filelist


def parse_profile(filepath):
    profile_lines = []
    is_record = False

    for line in open(filepath):
        if (line.lstrip('\t').rstrip('\n') == "# Files"):
            is_record = True
        if (line.lstrip('\t').rstrip('\n') == "# Implicit Rules"):
            is_record = False
        if ("# Finished Make data" in line.lstrip('\t').rstrip('\n')):
            is_record = False
        if ('CURDIR :=' in line):
            profile_lines.append(line)
            continue
        if ('make[' in line):
            continue
        if (not is_record):
            continue
        if (''.join(line).lstrip('\n').lstrip(' ') == ""):
            continue
        if ('=' in line):
            continue
        if (not ''.join(line).startswith('#') or 'Not a target' in line):
            profile_lines.append(line)
            continue
        if ('from' in line and 'line' in line):
            profile_lines.append(line)
            continue

    return profile_lines


def parse_profile_ninja(filepath):
    profile_lines = []
    for line in open(filepath):
        if line.strip('\t').strip('\n') != "":
            profile_lines.append(line)
            continue
    return profile_lines
