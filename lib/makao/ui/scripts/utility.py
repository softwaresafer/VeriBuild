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

from java.io import BufferedReader
from java.io import InputStreamReader
from javax.swing import JDialog


################################################
# find targets and/or edges based on the values of attributes #
################################################

def by_name(pattern):
    list=[]

    for node in g.nodes:
        if String(node.name).matches(String(pattern)):
            list.append(node)

    return list

def by_localname(pattern):
    list=[]

    for node in g.nodes:
        if String(node.localname).matches(String(pattern)):
            list.append(node)

    return list

def by_label(pattern):
    list=[]

    for node in g.nodes:
        if String(node.label).matches(String(pattern)):
            list.append(node)

    return list

def by_makefile(pattern):
    list=[]

    for node in g.nodes:
        if String(node.makefile).matches(String(pattern)):
            list.append(node)

    return list

def by_tstamp(stamp):
    return (tstamp==stamp)[0]

def node_at_tstamp(stamp):
    poss=[e for e in g.edges if e.tstamp==stamp]
    if len(poss)>0:
        return poss.node2[0]
    else:
        return None

def start_node():
    return (style==8)[0]

#####################
# graph-related functions #
#####################

#rewrite with dictionary for speed boost
def offspring(node):
    list=[]

    children=(node1==node).node2
    for child in set(children):
        if list.count(child)==0:
            list.append(child)
            list.extend([x for x in offspring(child) if list.count(x)==0])

    return list

def hide_hulls():
    for hull in getConvexHulls():
	hull.setVisible(false)

    return

def show_hulls():
    for hull in getConvexHulls():
	hull.setVisible(true)

    return

#pretty-printing command list of some target
def pp(target):
    print("\n".join(commands[target.name]))

    return

#pretty-printing actual command list of some target
def pp2(target):
    print("\n".join(actual_commands[target.name]))

    return

#pretty-printing macro list of some target
def pp3(target):
    if macros.has_key(target.name):
        print("\n".join(macros[target.name]))
    else:
        print("No active macros...")

    return

def relabel2tstamp():

    for node in g.nodes:
        node.label=str(node.tstamp)

def relabel2name():

    for node in g.nodes:
        node.label=str(node.name)

def relabel2localname():

    for node in g.nodes:
        node.label=str(node.localname)

#this is required to synchronize Prefuse's layouting with the in-memory model, otherwise saving does not pick up new co-ordinates
def sync():

    for n in g.nodes:
        n.x = n.x
        n.y = n.y

def save_and_exit(path):
    save(path)
    print "[LAYOUT SAVED] "+path+"-piccolo.gdf"
    Guess.shutdown()

def save_and_analyze(path):
   
    save(path)
    print "[LAYOUT SAVED] "+path+"-piccolo.gdf"
    try:
        f = open(gdf_dir_name+'/save_marker.bla','w')
        f.write(path+"-piccolo.gdf")
        f.close()
    except:
        print "Saving was successful, but you will need to manually start up MAKAO to analyze "+path+"-piccolo.gdf, since we had a small technical issue."
    Guess.shutdown()

def save(name):
    
    relabel2localname()
    sync()
    exportGDF(name+"-piccolo.gdf")

def using_tool(target,list):

    command_string=String("\n".join(commands[target.name]))
    
    for tool in list:
        if command_string.matches(String(".*(\n.*)*"+tool+".*(\n.*)*")):
            return true
        
    return false

def kill_orphans():

    remove([node for node in g.nodes if len(node.inEdges)==0 and len(node.outEdges)==0])
    return

#set of concerns of the dependencies of all nodes of aconcern
def concern_dep_concerns(aconcern):
    return set(flatten((concern==aconcern).outEdges.node2.concern))

#set of concerns of the nodes depending on nodes of aconcern
def concern_ref_concerns(aconcern):
    return set(flatten((concern==aconcern).inEdges.node1.concern))

#set of nodes of ref_node_concern depending on a node of dep_node_concern
def ref_nodes(ref_node_concern,dep_node_concern):
    return set([n for n in (concern==ref_node_concern) for d in n.outEdges.node2 if d.concern==dep_node_concern])

#set of nodes of dep_node_concern on which nodes of ref_node_concern depend
def dep_nodes(ref_node_concern,dep_node_concern):
    return set([d for n in (concern==ref_node_concern) for d in n.outEdges.node2 if d.concern==dep_node_concern])

#contains for each node number of incoming and outgoing edges
def coupling(nodes):
    return [[n,len(n.inEdges),len(n.outEdges)] for n in nodes]



###########################################
# general-purpose utility functions for data structures #
###########################################

def flip(bit):
    if bit==0:
	bit=1
    elif bit==1:
	bit=0
    else:
	raise RuntimeError('Bit cannot be different from 0 or 1!')

def flatten(list_of_lists):
     res=[]
     for l in list_of_lists:
            res=res+l
     return res
#    return [anelement for alist in list_of_lists
#	    for anelement in alist]

def set(alist):
    res=[]
    encountered={}

    for anelement in alist:
	if not encountered.has_key(anelement):
	    res.append(anelement)
	    encountered[anelement]=0

    return res

def concatenate_list_of_strings(list):

    def f(x,y): return x+y

    return reduce(f,list)

def pad_string(s,length,max_len):
    if len(s)>length:
        if len(s)<=max_len:
            return s
        else:
            return (s[:max_len-2] + '..')
    else:
        front=int((length-len(s))/2)
        back=length-len(s)-front

        front_s=" " * front
        back_s=" " * back
        return front_s+s+back_s


########################
# low-level visibility methods #
#######################
    
#show or hide a node/edge by itself, without transitively toggling connected nodes/edges
#otherwise, GUESS would use the following transitive rules:
            #if both nodes of edge become visible: GUESS shows invisible edges between them
            #if one of nodes of edge is invisible: GUESS hides visible edges between them

            #if edge becomes visible: make invisible end points visible
def toggle(node_or_edge,state):
    node_or_edge.getRep().set("visible",Boolean(state))
    node_or_edge.updateColumn("visible",Boolean(state))

def toggle_all(node_or_edges,state):
    for node_or_edge in node_or_edges:
        toggle(node_or_edge,state)
                                                    

#refactor to use the new toggling functions
def focus(nod):
    g.nodes.visible=0
    nod.visible=1
    nod.inEdges.node1.visible=1
    nod.outEdges.node2.visible=1
    tmp=[e for e in g.edges if e.node1!=nod and e.node2!=nod]
    tmp.visible=0

def expand(nod):
    nod.inEdges.node1.visible=1
    nod.outEdges.node2.visible=1
    tmp=[e for e in g.edges if e.node1!=nod and e.node2!=nod]
    tmp.visible=0
