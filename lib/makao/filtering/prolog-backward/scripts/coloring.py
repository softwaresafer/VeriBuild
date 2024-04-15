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

setDisplayBackground(black)

###########
# imports #
###########

execfile(makao_path+"ui/scripts/utility.py")
execfile(makao_path+"ui/scripts/file_filter.py")
execfile(makao_path+"ui/scripts/concern_sieve.py")
execfile(makao_path+"ui/scripts/weaver.py")
#execfile(makao_path+"filtering/prolog-backward/scripts/reducer.py")
#execfile(makao_path+"filtering/prolog-backward/scripts/reduce_command.py")
execfile(makao_path+"ui/scripts/xml_importer.py")
#execfile(makao_path+"filtering/prolog-backward/scripts/reifier.py")
execfile(makao_path+"filtering/prolog-backward/scripts/metrics.py")

#######
# GUI #
#######
sieve=concern_sieve()
#reduction_commando=reduce_command()

##########
# legend #
##########
if prefuse==0:
    xy=Legend()

def register_concern(nodes,concern):
    if len(nodes)==0:
        return

    if prefuse==0:
        xy.add(nodes[0],concern)

    sieve.register(concern)

def addConcern(aConcern,aColor):
    targets=(concern == aConcern)
    if len(targets) > 0:
	targets.color=aColor
#	concerns.append(targets)

        if prefuse==0:
            xy.add(targets[0],aConcern)

        sieve.register(aConcern)

###############################
# colorize different concerns #
###############################
crystal_home = crystal_path+"/128x128/"
#mainTarget = bzImage
#mainTarget = all


#g.edges.width = 3
#g.edges.color = darkgray

g.nodes.color = lightpurple

folders=(folder == true)
folders.image = crystal_home + "filesystems/folder_green.png"
folders.style = 7
folders.width = 15.0
folders.height = 15.0
folders.color = olivegreen
register_concern(folders,"folder")

#Java class
addConcern("class",brown)

#Java file
addConcern("java",green)

#Antlr g file
addConcern("g",lavender)

#C/C++ object
addConcern("o",red)

#a
addConcern("a",pinegreen)

#C/C++ header-file
addConcern("h",yellow)

#C++ header-file
addConcern("hpp",yellow)

#C file
addConcern("c",navyblue)

#ace
addConcern("ace",brown)

#frm
addConcern("frm",green)

#arc
addConcern("arc",cyan)

#per
addConcern("per",wildstrawberry)

#ec
addConcern("ec",melon)

#C++ file
addConcern("cpp",burntorange)

#lo
addConcern("lo",tan)

#la
addConcern("la",turquoise)

#am
addConcern("am",blueviolet)

#in
addConcern("in",wildstrawberry)

#m4
addConcern("m4",purple)

#all
addConcern("all",blue)

#FORCE
addConcern("FORCE",melon)

#sh
addConcern("sh",processblue)

#daj
addConcern("daj",dandelion)

#bsh
addConcern("bsh",seagreen)

#app
addConcern("app",plum)

#install
addConcern("install",fuchsia)

#pm
addConcern("pm",royalpurple)

#ucm
addConcern("ucm",darkgray)

#xs
addConcern("xs",forestgreen)

#so
addConcern("so",rawsienna)

#dylib
addConcern("dylib",rawsienna)

#PL
addConcern("PL",periwinkle)

#pl
addConcern("pl",goldenrod)

#bs
addConcern("bs",seagreen)

#S
addConcern("S",dandelion)

#s
addConcern("s",dandelion)

#component
addConcern("component",black)

#jar
addConcern("jar",pinegreen)

#pbc
addConcern("pbc",sepia)

#pir
addConcern("pir",orange)

#pmc
addConcern("pmc",aquamarine)

#pod
addConcern("pod",mulberry)

#os=(concern == "o")
#os.image = crystal_home + "mimetypes/source_o.png"
#os.style = 7
#os.color = red
#register_concern(os,"o")
#
#cs=(concern == "c")
#cs.image = crystal_home + "mimetypes/source_c.png"
#cs.style = 7
#cs.color = navyblue
#register_concern(cs,"c")

c_shippeds=(concern == "c_shipped")
c_shippeds.image = crystal_home + "mimetypes/source_c.png"
c_shippeds.style = 7
c_shippeds.color = cornflowerblue
register_concern(c_shippeds,"c_shipped")

#shs = (concern=="sh")
#shs.image = crystal_home + "mimetypes/shellscript.png"
#shs.style = 7
#shs.color = processblue
#register_concern(shs,"sh")
#
##(concern == "ec").image = crystal_home + "actions/db_comit.png"
#ecs=(concern == "ec")
#ecs.image = crystal_home + "mimetypes/spreadsheet.png"
#ecs.style = 7
#ecs.color = midnightblue
#register_concern(ecs,"ec")
#
#hs=(concern == "h")
#hs.image = crystal_home + "mimetypes/source_h.png"
#hs.style = 7
#hs.color = yelloworange
#register_concern(hs,"h")

h_shippeds=(concern == "h_shipped")
h_shippeds.image = crystal_home + "mimetypes/source_h.png"
h_shippeds.style = 7
h_shippeds.color = goldenrod
register_concern(h_shippeds,"h_shipped")

#sss=(concern == "s")
#sss.image = crystal_home + "mimetypes/source_s.png"
#sss.style = 7
#sss.color = bittersweet
#register_concern(sss,"s")
#
#SSS=(concern == "S")
#SSS.image = crystal_home + "mimetypes/source_s.png"
#SSS.style = 7
#SSS.color = bittersweet
#register_concern(SSS,"S")

bins=(concern == "bin")
bins.image = crystal_home + "mimetypes/binary.png"
bins.style = 7
bins.color = plum
register_concern(bins,"bin")

gzs=(concern == "gz")
gzs.image = crystal_home + "apps/kthememgr.png"
gzs.style = 7
gzs.color = brown
register_concern(gzs,"gz")

#sos=(concern == "so")
#sos.image = crystal_home + "mimetypes/man.png"
#sos.style = 7
#sos.color = orangered
#register_concern(sos,"so")
#
#dylibs=(concern == "dylib")
#dylibs.image = crystal_home + "mimetypes/man.png"
#dylibs.style = 7
#dylibs.color = orangered
#register_concern(dylibs,"dylib")
#
#aas=(concern == "a")
#aas.image = crystal_home + "mimetypes/man.png"
#aas.style = 7
#aas.color = mulberry
#register_concern(aas,"a")

cmds=(concern == "cmd")
cmds.image = crystal_home + "apps/terminal.png"
cmds.style = 7
cmds.color = emerald
register_concern(cmds,"cmd")

unis=(concern == "uni")
unis.image = crystal_home + "apps/kcharselect.png"
unis.style = 7
unis.color = turquoise
register_concern(unis,"uni")

ldss=(concern == "lds")
ldss.image = crystal_home + "mimetypes/template_source.png"
ldss.style = 7
ldss.color = rubinered
register_concern(ldss,"lds")

configs=(concern == "config")
configs.color=blue
register_concern(configs,"config")

memorys=(concern == "memory")
memorys.color=green
register_concern(memorys,"memory")

representations=(concern == "representation")
representations.color=red
register_concern(representations,"representation")

compilations=(concern == "compilation")
compilations.color=cyan
register_concern(compilations,"compilation")

bytecodes=(concern == "bytecode")
bytecodes.color=goldenrod
register_concern(bytecodes,"bytecode")

schedulings=(concern == "scheduling")
schedulings.color=brown
register_concern(schedulings,"scheduling")

oss=(concern == "os")
oss.color=orange
register_concern(oss,"os")

executions=(concern == "execution")
executions.color=periwinkle
register_concern(executions,"execution")

embeds=(concern == "embed")
embeds.color=royalblue
register_concern(embeds,"embed")

utils=(concern == "util")
utils.color=gray
register_concern(utils,"util")

#testings=(concern == "testing")
#testings.color=fuchsia
#register_concern(testings,"testing")

jits=(concern == "jit")
jits.color=fuchsia
register_concern(jits,"jit")

debugs=(concern=="debug")
debugs.color=emerald
register_concern(debugs,"debug")

#(component == true).image = crystal_home + "apps/ark2.png"
#(component == true).style = 7
#(component == true).width = 15.0
#(component == true).height = 15.0

#(label like "%linux").image = crystal_home + "apps/tux.png"
#(label like "%linux").style = 7
#(label like "%linux").width = 20.0
#(label like "%linux").height = 20.0
#
#(label like "%/all").image = crystal_home + "apps/flag.png"
#(label like "%/all").style = 7
#(label like "%/all").color = blue
#
#(label like "%/install").image = crystal_home + "apps/flag.png"
#(label like "%/install").style = 7
#(label like "%/install").color = blue

mainTarget.image = crystal_home + "filesystems/folder_home.png"
mainTarget.style = 7
mainTarget.width = 25.0
mainTarget.height = 25.0

##############
# edge color #
##############
for e in g.edges: e.color = e.node2.color

#g.gemLayout()
center

######################
# import target data #
######################
commands=0
try:
    res=xml_importer(false,makao_path+"/filtering/prolog-backward/experiments").parse_file()
    commands=res[0]
    actual_commands=res[1]
except RuntimeError:
    print "ERROR: XML import did NOT succeed!\n"

######################
# relabel in Prefuse #
######################

name_to_labels={}

def relabel2name():

    for node in g.nodes:
        name_to_labels[node.name]=node.label
        node.label=str(node.name)

def relabel2label():
    
    for node in g.nodes:
        node.label=name_to_labels[node.name]

def export2piccolo2(name):
    
    relabel2label()
    sync()
    g.nodes.style=2
    g.nodes.image=""
    exportGDF(name+"-piccolo.gdf")

if prefuse==1:
    relabel2name()

#clusts = groupBy(makefile)
#for c in clusts: createConvexHull(c,randomColor(120))

####################
# add context menu #
####################

execfile(makao_path+"ui/scripts/context_menus.py")

#change node style in case of platform-specific nodes
#(arch==true).style=3
#(os==true).style=3

import math

tenlog=math.log(10)
for e in g.edges:
   e.width=math.log(e.weight)/tenlog*2
 
