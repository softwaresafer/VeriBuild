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

from javax.swing import JCheckBox
from com.hp.hpl.guess.ui import DockableAdapter
#from java.lang import System

#Interactive enabling/disabling of concerns
class concern_sieve:

    def __init__(self):

        self.concerns=[]
        self.view=concern_checkbox_group('Target Filter')
        #used to sync boxes with current visibility without issueing events
        self.synchronizing=false

    def toggle(self,aconcern):

        if self.concerns.count(aconcern) == 0:
            raise RuntimeError('Concern not registered!')
        elif self.synchronizing == true:
            return
        else:
            #do not let the check.selected=... trigger an event
            self.synchronizing = true

        nodes=(concern == aconcern)
        visible_nodes=filter(lambda node: node.visible==1,nodes)

        #hiding a node would also hide its edges, so here we immediately hide the edges, which implicitly hides the node
        all_visible_edges=visibilizer.visible_population()
        the_edges=set(flatten(nodes.inEdges + nodes.outEdges)) & all_visible_edges

        check=self.view.concern_to_checkboxes[aconcern]

        if len(visible_nodes) == 0:
            #update display
            check.selected=visibilizer.toggle(false,the_edges)
#        (concern == aconcern).visible=1
#        check.selected=true
        else:
            #update display
            check.selected=visibilizer.toggle(true,the_edges)
#        (concern == aconcern).visible=0
#        check.selected=false

        #System.err.println(String("Nodes: "+`len(nodes)`+" <--> Visible: "+`len(visible_nodes)`))
        #false event alarm passed
        self.synchronizing = false

    def register(self,aconcern):

        #let toggle do all the work
        if self.concerns.count(aconcern) == 0:
	    self.concerns.append(aconcern)
            self.view.addConcern(aconcern)
            #self.toggle(aconcern)
        else:
            raise RuntimeError('Concern was already registered!')

    def unregister(self,aconcern):

        if self.concerns.count(aconcern) == 0:
            raise RuntimeError('Concern was not registered yet!')
        else:
            self.concerns.remove(aconcern)
            self.view.removeConcern(aconcern)
	    g.nodes.visible=1

class concern_checkbox_group(DockableAdapter):

    def __init__(self,new_title):

        self.atitle=new_title
        self.concern_to_checkboxes={}
        centerButton = JButton("CENTER")
        centerButton.setForeground(Color.RED)
        centerButton.actionPerformed = lambda event: v.center()
        self.add(centerButton)

        self.revalidate()
        self.repaint()
        ui.dock(self)

    def addConcern(self,aconcern):

        check=JCheckBox(aconcern)
        check.selected=true
        check.itemStateChanged = lambda event: sieve.toggle(event.itemSelectable.text)
        self.add(check)
        self.revalidate()
        self.repaint()
        self.concern_to_checkboxes[aconcern]=check

    def removeConcern(self,aconcern):

        if self.concern_to_checkboxes.has_key(aconcern) == false:
            raise RuntimeError('Cannot remove checkbox, as concern was not registered yet!')
        else:
            self.remove(self.concern_to_checkboxes[aconcern])
            self.revalidate()
            self.repaint()
            del self.concern_to_checkboxes[aconcern]
        
    def getTitle(self):

        # define the title in the window
        return('%s' % self.atitle)
