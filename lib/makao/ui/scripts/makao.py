# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is MAKAO.
#
# The Initial Developer of the Original Code is
# Bram Adams (bramATcsDOTqueensuDOTca).
# Portions created by the Initial Developer are Copyright (C) 2006-2010
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#
# ***** END LICENSE BLOCK *****

#setDisplayBackground(white)
setDisplayBackground(black)
g.nodes.color=lightpurple
#g.edges.width=.3

###########
# imports #
###########
execfile(makao_path+"ui/scripts/utility.py")
execfile(makao_path+"ui/scripts/shapes.py")
execfile(makao_path+"ui/scripts/file_filter.py")
execfile(makao_path+"ui/scripts/xml_importer.py")

if prefuse==0:
    execfile(makao_path+"ui/scripts/concern_sieve.py")
    execfile(makao_path+"ui/scripts/visibility_control.py")
    #execfile(makao_path+"ui/scripts/weaver.py")
    #execfile(makao_path+"filtering/prolog-forward/scripts/reducer.py")
    #execfile(makao_path+"filtering/prolog-forward/scripts/reduce_command.py")
    execfile(makao_path+"ui/scripts/replay.py")
    execfile(makao_path+"ui/scripts/slider.py")
    #execfile(makao_path+"filtering/prolog-forward/scripts/reifier.py")
else:
    execfile(makao_path+"ui/scripts/prefuse_actions.py")

#######
# GUI #
#######
if prefuse==0:
    sieve=concern_sieve()
    debugger=slider()
    visibilizer=visibility_control()
else:
    prefuser=prefuse_actions()
#reduction_commando=reduce_command()

################
# create hulls #
################
clusts = []
if enable_hulls==1:
    clusts = (visible==1).groupBy(makefile)
    for c in clusts: createConvexHull(c,randomColor(120))

###############################
# colorize different concerns #
###############################
concerns=[]
#nodes_in_identified_concern=[]

def addConcern(concerns,aConcern,aColor):
    targets=(concern == aConcern)
#    nodes_in_identified_concern.extend(targets)
    if len(targets) > 0:
        targets.color=aColor
        concerns.append(targets)

def addBaseLegend(concerns):
    #Java class
    addConcern(concerns,"class",brown)

    #Java file
    addConcern(concerns,"java",green)

    #Antlr g file
    addConcern(concerns,"g",lavender)

    #C/C++ object
    addConcern(concerns,"o",red)

    #a
    addConcern(concerns,"a",pinegreen)

    #C/C++ header-file
    addConcern(concerns,"h",yellow)

    #C++ header-file
    addConcern(concerns,"hpp",yellow)

    #C file
    addConcern(concerns,"c",navyblue)

    #Fortran file
    addConcern(concerns,"f",green)

    #ace
    addConcern(concerns,"ace",brown)

    #frm
    addConcern(concerns,"frm",green)

    #arc
    addConcern(concerns,"arc",cyan)

    #per
    addConcern(concerns,"per",wildstrawberry)

    #ec
    addConcern(concerns,"ec",melon)

    #C++ file
    addConcern(concerns,"cpp",burntorange)

    #lo
    addConcern(concerns,"lo",tan)

    #la
    addConcern(concerns,"la",turquoise)

    #am
    addConcern(concerns,"am",blueviolet)

    #in
    addConcern(concerns,"in",wildstrawberry)

    #m4
    addConcern(concerns,"m4",purple)

    #all
    addConcern(concerns,"all",blue)

    #FORCE
    addConcern(concerns,"FORCE",melon)

    #sh
    addConcern(concerns,"sh",processblue)

    #daj
    addConcern(concerns,"daj",dandelion)

    #bsh
    addConcern(concerns,"bsh",seagreen)

    #app
    addConcern(concerns,"app",plum)

    #install
    addConcern(concerns,"install",fuchsia)

    #pm
    addConcern(concerns,"pm",royalpurple)

    #ucm
    addConcern(concerns,"ucm",darkgray)

    #xs
    addConcern(concerns,"xs",forestgreen)

    #so
    addConcern(concerns,"so",rawsienna)

    #dylib
    addConcern(concerns,"dylib",black)

    #PL
    addConcern(concerns,"PL",periwinkle)

    #pl
    addConcern(concerns,"pl",goldenrod)

    #bs
    addConcern(concerns,"bs",seagreen)

    #S
    addConcern(concerns,"S",dandelion)

    #s
    addConcern(concerns,"s",dandelion)

    #component
    addConcern(concerns,"component",black)

    #jar
    addConcern(concerns,"jar",pinegreen)

    #pbc
    addConcern(concerns,"pbc",sepia)

    #pir
    addConcern(concerns,"pir",orange)

    #pmc
    addConcern(concerns,"pmc",aquamarine)

    #pod
    addConcern(concerns,"pod",mulberry)

addBaseLegend(concerns)

##########
# legend #
##########
if prefuse==0:
    xy=Legend()

for c in concerns:
    if prefuse==0:
        xy.add(c[0],c[0].concern)

        sieve.register(c[0].concern)

##############
# edge color #
##############
for e in g.edges: e.color=e.node2.color

center

######################
# import target data #
######################
commands=0
actual_commands=0
macros=0
try:
    res=xml_importer(false,makao_path+"/apps").parse_file()
    commands=res[0]
    actual_commands=res[1]
    macros=res[2]
except RuntimeError:
    print "ERROR: XML import did NOT succeed!\n"

######################
# relabel in Prefuse #
######################
if prefuse==1:
    relabel2tstamp()

####################
# add context menu #
####################

execfile(makao_path+"ui/scripts/context_menus.py")
