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
# Portions created by the Initial Developer are Copyright (C) 2007-2010
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#
# ***** END LICENSE BLOCK *****

class replay:

    def __init__(self):

        self.edge_dictionary = {}
        self.index_edges()

        self.min_tstamp=-1
        self.max_tstamp=max(g.edges.tstamp)
        self.current_tstamp=self.max_tstamp

    def index_edges(self):
        
        for e in g.edges:
            self.edge_dictionary[e.tstamp]=e

    def reset_to_max(self):

        g.nodes.visible=1
        g.edges.visible=1
        self.current_tstamp=self.max_tstamp
        debugger.testSlider.setValue(self.current_tstamp)

    def reset_to_min(self):

        g.nodes.visible=0
        g.edges.visible=0

        #make start node visible, just in case
        toggle(start_node(),1)

        self.current_tstamp=self.min_tstamp
        debugger.testSlider.setValue(self.current_tstamp)

    def next_existing_tstamp(self,atstamp):
        atstamp=atstamp+1
        while (atstamp<=self.max_tstamp) and not (self.edge_dictionary.has_key(atstamp)):
            atstamp=atstamp+1

        if atstamp>self.max_tstamp:
            return self.max_tstamp+1
        else:
            return atstamp

    def prev_existing_tstamp(self,atstamp):
        atstamp=atstamp-1
        while (atstamp>=0) and not (self.edge_dictionary.has_key(atstamp)):
            atstamp=atstamp-1

        if atstamp<0:
            return -1
        else:
            return atstamp
      
    def goto(self,atstamp,verbose):
        if atstamp==self.current_tstamp:
            return
        elif atstamp<self.current_tstamp:
            self.goback(atstamp,verbose)
            return
        else:
            while self.current_tstamp<atstamp:
                next_tstamp=self.next_existing_tstamp(self.current_tstamp)
                self.current_tstamp=next_tstamp

                if self.current_tstamp>self.max_tstamp:
                    self.current_tstamp=self.max_tstamp
                    return
                
                e=self.edge_dictionary[self.current_tstamp]
                toggle(e,1)
                toggle(e.node2,1)

                debugger.update_label(str(e.tstamp)+": "+e.node1.label+" -> "+e.node2.label)
                if verbose:
                    print "showing dependency from "+e.node1.name+" to "+e.node2.name+": "+e.node1.label+" -> "+e.node2.label
                debugger.testSlider.setValue(self.current_tstamp)

            return

    def goback(self,atstamp,verbose):
#        print "go from "+str(self.current_tstamp)+" to "+str(atstamp)
        
        if atstamp==self.current_tstamp:
            return
        elif atstamp>self.current_tstamp:
            self.goto(atstamp,verbose)
            return
        else:
#            self.current_tstamp=self.current_tstamp+1 #make sure that current current_tstamp is treated
            
            while self.current_tstamp>atstamp:
                e=self.edge_dictionary[self.current_tstamp]
                toggle(e,0)
                        
                tmp2=[ed for ed in e.node2.inEdges if ed.visible==1]
                tmp3=[ed for ed in e.node2.outEdges if ed.visible==1]
                if len(tmp2)==0 and len(tmp3)==0:
                    toggle(e.node2,0)

                debugger.update_label(str(e.tstamp)+": "+e.node1.label+" -> "+e.node2.label)
                if verbose:
                    print "hiding dependency from "+e.node1.name+" to "+e.node2.name+": "+e.node1.label+" -> "+e.node2.label

                prev_tstamp=self.prev_existing_tstamp(self.current_tstamp)
                self.current_tstamp=prev_tstamp
                debugger.testSlider.setValue(self.current_tstamp)

                if self.current_tstamp<0:
                    return

            return

    def next(self,stride,verbose):

        for i in range(1,stride+1):
            self.goto(self.next_existing_tstamp(self.current_tstamp),verbose)


    def prev(self,stride,verbose):

        for i in range(1,stride+1):
            self.goto(self.prev_existing_tstamp(self.current_tstamp),verbose)

