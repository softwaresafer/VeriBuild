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

#calculate number of incoming edges from different nodes, sort and print
def calc_scattering():
    results=[]
    all_concerns=set(g.nodes.concern)
    
    #for all nodes
    for n in g.nodes:
        print n.name

        cnt=0
#UNNEEDED: no double edges        checked_node1s=[]
        concern_to_count={}
        in_edges=n.inEdges

        for c1 in all_concerns:
            concern_to_count[c1]=0

        for n1 in in_edges.node1:

            #if checked_node1s.count(n1)==0:
            #    checked_node1s.append(n1)
            cnt=cnt+1
                
#            if concern_to_count.has_key(n1.concern):
            concern_to_count[n1.concern]=concern_to_count[n1.concern]+1
#                else:
#                    concern_to_count[n1.concern]=1

        #count number of concerns used
        concerns_used=0
        for c1 in concern_to_count.keys():
            co=concern_to_count[c1]

            if co > 0:
                concerns_used=concerns_used+1
        
        results.append((n,cnt,concerns_used))

    res=[(node,node.concern,incoming,cs) for (node,incoming,cs) in results if incoming>0]
    res.sort(lambda x,y:cmp(x[2],y[2]))

    return res

#calculate number of outgoing edges to different nodes, sort and print
def calc_tangling():
    results=[]
    all_concerns=set(g.nodes.concern)
    
    #for all nodes
    for n in g.nodes:
        print n.name

        cnt=0
#UNNEEDED: no double edges        checked_node1s=[]
        concern_to_count={}
        out_edges=n.outEdges

        for c1 in all_concerns:
            concern_to_count[c1]=0

        for n2 in out_edges.node2:

            #if checked_node1s.count(n1)==0:
            #    checked_node1s.append(n1)
            cnt=cnt+1
                
#            if concern_to_count.has_key(n1.concern):
            concern_to_count[n2.concern]=concern_to_count[n2.concern]+1
#                else:
#                    concern_to_count[n1.concern]=1

        #count number of concerns used
        concerns_used=0
        for c1 in concern_to_count.keys():
            co=concern_to_count[c1]

            if co > 0:
                concerns_used=concerns_used+1
        
        results.append((n,cnt,concerns_used))

    res=[(node,node.concern,outgoing,cs) for (node,outgoing,cs) in results if outgoing>0]
    res.sort(lambda x,y:cmp(x[2],y[2]))

    return res
