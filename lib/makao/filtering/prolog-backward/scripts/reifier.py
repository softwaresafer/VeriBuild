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

from jpl import Query

class reifier:

    def __init__(self,debug):

	self.debug=debug
#        Query(String("consult('"+makao_path+"rules/prolog/main.pl')")).oneSolution()
#        Query(String("consult('"+makao_path+"rules/prolog/utility.pl')")).oneSolution()

    def reify(self):

        print "Reifying graph...\n"

        query="assert(node_fields(['name','localname VARCHAR(255)','makefile VARCHAR(255)','line INT','style','concern VARCHAR(50)','error INT','tstamp INT','phony INT','dir VARCHAR(255)','base VARCHAR(255)','inuse INT']))"
        Query(String(query)).oneSolution()

        for node in g.nodes:
            query="assert(node('%s','%s','%s',%d,%d,'%s',%d,%d,%d,'%s','%s',%d))" % (node.name,node.localname,node.makefile,node.line,node.style,node.concern,node.error,node.tstamp,node.phony,node.dir,node.base,node.inuse)
            Query(String(query)).oneSolution()

        query="assert(edge_fields(['node1','node2','directed','ismeta INT','tstamp INT','pruning INT','implicit INT']))"
        Query(String(query)).oneSolution()

        for edge in g.edges:
            query="assert(edge('%s','%s',%d,%d,%d,%d,%d))" % (edge.node1.name,edge.node2.name,edge.directed,edge.ismeta,edge.tstamp,edge.pruning,edge.implicit)
            Query(String(query)).oneSolution()
            query="assert(redge('%s','%s',%d,%d,%d,%d,%d))" % (edge.node2.name,edge.node1.name,edge.directed,edge.ismeta,edge.tstamp,edge.pruning,edge.implicit)
            Query(String(query)).oneSolution()

            
