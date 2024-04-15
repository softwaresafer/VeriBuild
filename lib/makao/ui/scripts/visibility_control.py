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
# Portions created by the Initial Developer are Copyright (C) 2014
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#
# ***** END LICENSE BLOCK *****

from javax.swing import JCheckBox
from com.hp.hpl.guess.ui import DockableAdapter
from javax.swing.event import ChangeListener
#from java.lang import System

#master visibility control
class visibility_control:

    def __init__(self):

        self.first_phase=true
        self.second_phase=true
        self.implicit=true

        self.view=visibility_checkbox_group('Visibility Control')

    #full population that potentially can be visible
    def visible_population(self):
        res=[]
        if self.first_phase:
            res.extend((ismeta==1)&(implicit==0))
        if self.second_phase:
            res.extend((ismeta==0)&(implicit==0))
        if self.implicit:
            res.extend((implicit==1))

        return res

    def toggle_first_phase(self):
        self.first_phase=self.toggle(self.first_phase,(ismeta==1)&(implicit==0))
#        if self.second_phase:
#            for e in (ismeta==0)&(implicit==0):
#                if e.visible==0:
#                    raise RuntimeError("12: "+e)
#        if self.implicit:
#            for e in (implicit==1):
#                if e.visible==0:
#                    raise RuntimeError("13: "+e)

    def toggle_second_phase(self):
        self.second_phase=self.toggle(self.second_phase,(ismeta==0)&(implicit==0))
#        if self.first_phase:
#            for e in (ismeta==1)&(implicit==0):
#                if e.visible==0:
#                    raise RuntimeError("21: "+e)
#        if self.implicit:
#            for e in (implicit==1):
#                if e.visible==0:
#                    raise RuntimeError("23: "+e)

    def toggle_implicit(self):
        self.implicit=self.toggle(self.implicit,(implicit==1))
#        if self.first_phase:
#            for e in (ismeta==1)&(implicit==0):
#                  if e.visible==0:
#                    raise RuntimeError("31: "+e)
#        if self.second_phase:
#            for e in (ismeta==0)&(implicit==0):
#                if e.visible==0:
#                    raise RuntimeError("32: "+e)

    def toggle(self,condition_state,list_edges):
        the_edges=list_edges
        if len(the_edges)==0:
            return condition_state

        if condition_state:
            #hide stuff
            for e in the_edges:
                toggle(e,0)

            #set is necessary to reduce #nodes (and hence #edges) significantly
            relevant_nodes=set(the_edges.node1 + the_edges.node2)
            the_orphans=[node for node in relevant_nodes
                         if (len(node.inEdges)>=0 and len([e for e in node.inEdges if e.visible==1])==0)
                         and (len(node.outEdges)>=0 and len([e for e in node.outEdges if e.visible==1])==0)
                         ]
            
            if len(the_orphans)>0:
                for n in the_orphans:
                    toggle(n,0)

        else:
            #show stuff
            for e in the_edges:
                toggle(e,1)

            #set is necessary to reduce #nodes (and hence #edges) significantly
            relevant_nodes=set(the_edges.node1 + the_edges.node2)

            for node in relevant_nodes:
                toggle(node,1)
        
        return 1-condition_state


class visibility_checkbox_group(DockableAdapter):

    def __init__(self,new_title):

        self.atitle=new_title

        centerButton = JButton("CENTER")
        centerButton.setForeground(Color.RED)
        centerButton.actionPerformed = lambda event: v.center()
        self.add(centerButton)

        first_phase=JCheckBox("Show Dependency Graph Construction")
        first_phase.selected=true
        first_phase.itemStateChanged = lambda event: visibilizer.toggle_first_phase()
        self.add(first_phase)

        second_phase=JCheckBox("Show Actual Construction")
        second_phase.selected=true
        second_phase.itemStateChanged = lambda event: visibilizer.toggle_second_phase()
        self.add(second_phase)

        implicit=JCheckBox("Show Detected Implicit Dependencies")
        implicit.selected=true
        implicit.itemStateChanged = lambda event: visibilizer.toggle_implicit()
        self.add(implicit)

        self.revalidate()
        self.repaint()
        ui.dock(self)

        self.getParent().addChangeListener(MAKAOChangeListener())
      
    def getTitle(self):

        # define the title in the window
        return('%s' % self.atitle)

class MAKAOChangeListener(ChangeListener):

    def __init__(self):
        self.visible_nodes=[]
        self.visible_edges=[]
        self.debugger_previously_selected=false

    def stateChanged(self,changeEvent):
        sourceTabbedPane=changeEvent.getSource()
        index = sourceTabbedPane.getSelectedIndex();

        if sourceTabbedPane.getTitleAt(index)==debugger.getTitle():
            if not self.debugger_previously_selected:
                print "Switching to debugger mode, so storing currently visible nodes and edges"
                self.visible_nodes=[n for n in g.nodes if n.visible==1]
                self.visible_edges=[n for n in g.edges if n.visible==1]

                debugger.reset()
                self.debugger_previously_selected=true
        else:
            if sourceTabbedPane.getTitleAt(index)!="Interpreter":
                if self.debugger_previously_selected:
                    print "Leaving debugger mode, so restoring previously visible nodes and edges"
                    g.nodes.visible=0
                    g.edges.visible=0
                    toggle_all(self.visible_nodes,1)
                    toggle_all(self.visible_edges,1)
                    self.visible_nodes=[]
                    self.visible_edges=[]
                
                self.debugger_previously_selected=false
            
