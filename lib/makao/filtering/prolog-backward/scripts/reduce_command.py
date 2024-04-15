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

from java.awt.event import KeyEvent
from com.hp.hpl.guess.ui import DockableAdapter
from java.awt import Color
from java.awt import Component
from javax.swing.event import ListSelectionListener
from javax.swing import DefaultListModel
from javax.swing import JScrollPane
from javax.swing import BoxLayout
from javax.swing import JDialog

#Reduction/abstraction of graph
#load_button | rule_list and -_model | add_- and remove_button | scheduled_rule_list and -_model | run_button
class reduce_command(DockableAdapter):

    def __init__(self):

        self.a_reducer=reducer()

        self.start_state_name="blablabla"
        self.end_state_name="blobloblo"

        self.atitle="Reduction Commando Center"

        self.load_button = JButton("Load...")
        self.load_button.setVerticalTextPosition(AbstractButton.CENTER)
        self.load_button.setHorizontalTextPosition(AbstractButton.LEADING) #aka LEFT, for left-to-right locales
        self.load_button.setMnemonic(KeyEvent.VK_L)#L button
        self.load_button.setActionCommand("load")
        self.load_button.setToolTipText("Click this button to load a Prolog file.")
        self.load_button.actionPerformed=lambda event: reduction_commando.load_prolog_files()
        self.add(self.load_button)

        self.rule_list_model = DefaultListModel()
        self.rule_list = JList(self.rule_list_model)
        self.rule_list.valueChanged=lambda event: 1 #self.select_rules(event)
        self.rule_list.setVisibleRowCount(5)
        self.add(JScrollPane(self.rule_list))
        self.selected_rules=[]

        pane=JPanel()
        pane.setLayout(BoxLayout(pane, BoxLayout.Y_AXIS));
        self.add_button = JButton("Add...")
        self.add_button.setVerticalTextPosition(AbstractButton.CENTER)
        self.add_button.setHorizontalTextPosition(AbstractButton.LEADING) #aka LEFT, for left-to-right locales
        self.add_button.setMnemonic(KeyEvent.VK_A)#A button
        self.add_button.setActionCommand("add")
        self.add_button.setToolTipText("Click this button to add a rule to the selection.")
        self.add_button.actionPerformed=lambda event: reduction_commando.add_prolog_rules()
        self.add_button.setEnabled(false);
        self.add_button.setAlignmentX(Component.CENTER_ALIGNMENT);
        pane.add(self.add_button);

        self.remove_button = JButton("Remove...")
        self.remove_button.setVerticalTextPosition(AbstractButton.CENTER)
        self.remove_button.setHorizontalTextPosition(AbstractButton.LEADING) #aka LEFT, for left-to-right locales
        self.remove_button.setMnemonic(KeyEvent.VK_A)#A button
        self.remove_button.setActionCommand("remove")
        self.remove_button.setToolTipText("Click this button to remove a rule from the selection.")
        self.remove_button.actionPerformed=lambda event: reduction_commando.remove_prolog_rules()
        self.remove_button.setEnabled(false);
        self.remove_button.setAlignmentX(Component.CENTER_ALIGNMENT);
        pane.add(self.remove_button);
        self.add(pane)

        self.scheduled_rule_list_model = DefaultListModel()
        self.scheduled_rule_list = JList(self.scheduled_rule_list_model)
        self.scheduled_rule_list.valueChanged=lambda event: 1 #self.select_scheduled_rules(event)
        self.scheduled_rule_list.setVisibleRowCount(5)
        self.add(JScrollPane(self.scheduled_rule_list))
        self.selected_scheduled_rules=[]

        self.run_button = JButton("Run...")
        self.run_button.setVerticalTextPosition(AbstractButton.CENTER)
        self.run_button.setHorizontalTextPosition(AbstractButton.LEADING) #aka LEFT, for left-to-right locales
        self.run_button.setMnemonic(KeyEvent.VK_A)#A button
        self.run_button.setActionCommand("run")
        self.run_button.setToolTipText("Click this button to run a rule from the selection.")
        self.run_button.actionPerformed=lambda event: reduction_commando.run_prolog_rules()
        self.run_button.setEnabled(false);
        self.run_button.setBackground(Color.red)
        self.run_button.setForeground(Color.blue)
        self.add(self.run_button)

#        self.initialize_dialog(false)
        #Create the dialog.
        self.dialog = JDialog(ui,"What do you want to do?")

        #Add contents to it. It must have a close button,
        #since some L&Fs (notably Java/Metal) don't provide one
        #in the window decorations for dialogs.
        label = JLabel("<html><p align=center>Are you satisfied with this reduction?</p></center>")
        label.setHorizontalAlignment(JLabel.CENTER)

        yesButton = JButton("Yes");
        yesButton.actionPerformed=lambda event:yes_action(event)

        noButton = JButton("No");
        noButton.actionPerformed=lambda event:no_action(event)

        panel = JPanel();
        panel.setLayout(BoxLayout(panel,BoxLayout.LINE_AXIS))
        panel.add(Box.createHorizontalGlue());
        panel.add(yesButton);
        panel.add(noButton);
        panel.setBorder(BorderFactory.createEmptyBorder(0,0,5,5))

        contentPane = JPanel(BorderLayout())
        contentPane.add(label, BorderLayout.CENTER);
        contentPane.add(panel, BorderLayout.PAGE_END);
        contentPane.setOpaque(true);
        self.dialog.setContentPane(contentPane);

        #Show it.
        self.dialog.setSize(Dimension(300, 150));
        self.dialog.setLocationRelativeTo(ui.getContentPane());
        self.dialog.setVisible(false);

        self.revalidate()
        self.repaint()
        ui.dock(self)

    def getTitle(self):

        # define the title in the window
        return('%s' % self.atitle)

    # add new rules to rule_list_model and enable add_- and remove_buttons
    def load_prolog_files(self):
        
#        a_reducer.initialize()
        new_rules=self.a_reducer.readPrologFiles([])
        number_of_old_rules=self.rule_list_model.size()
        for rule in new_rules:
            if not(self.rule_list_model.contains(rule)):
                self.rule_list_model.addElement(rule)
                
        if number_of_old_rules==0 and self.rule_list_model.size()>0:
            self.add_button.setEnabled(true)
                    
    # add selected rules of rule_list_model to scheduled_rule_list_model and enable remove_- and run_buttons
    def add_prolog_rules(self):
        
        number_of_old_rules=self.scheduled_rule_list_model.size()
        for rule in self.rule_list.getSelectedValues():
            self.scheduled_rule_list_model.addElement(rule)
            
        if number_of_old_rules==0 and self.scheduled_rule_list_model.size()>0:
            self.remove_button.setEnabled(true)
            self.run_button.setEnabled(true)
                
    # remove selected rules from scheduled_rule_list_model and possibly disable remove_- and run_buttons
    def remove_prolog_rules(self):
        
        number_of_old_rules=self.scheduled_rule_list_model.size()
        index=0
        for rule in self.scheduled_rule_list.getSelectedIndices():
            self.scheduled_rule_list_model.removeElementAt(rule-index)
            index=index+1
            
        if self.scheduled_rule_list_model.size()==0 and number_of_old_rules>0:
            self.remove_button.setEnabled(false)
            self.run_button.setEnabled(false)

    # run selected rules from scheduled_rule_list_model and afterwards disable remove_- and run_buttons
    def run_prolog_rules(self):
        
#        print "Do something...\n"
        #just hide nodes/edges, change attributes and add new nodes/edges
        #then, ask whether this is OK => permanently delete hidden nodes/edges
        #otherwise, restore old situation
        #javax.swing.SwingUtilities.invokeLater(blinker())
        solutions=[]

        for rule in self.scheduled_rule_list_model.elements():
            query="catch(reduce_ui_rule('%s',NewNodes,NewEdges,RemovedNodes,RemovedEdges,ReplacedNodes,ReplacedEdges),E,(print_message(error,E),fail))" % (rule)
            solutions.append(Query(query).allSolutions())
#            res=[]

#            if aHashMap.size()>1:
#                raise RuntimeError("Rule "+rule+" should not yield more than one solution!")

        ss(self.start_state_name)

        for aHashMap in solutions:
            for entry in aHashMap:
            
                new_nodes=entry.get("NewNodes").toTermArray()
                removed_nodes=entry.get("RemovedNodes").toTermArray()
                replaced_nodes=entry.get("ReplacedNodes").toTermArray()
                new_edges=entry.get("NewEdges").toTermArray()
                removed_edges=entry.get("RemovedEdges").toTermArray()
                replaced_edges=entry.get("ReplacedEdges").toTermArray()
                
                self.handle_effects_of_rule(new_nodes,removed_nodes,replaced_nodes,new_edges,removed_edges,replaced_edges)

        ss(self.end_state_name)
        self.dialog.setVisible(true)
                    
        self.scheduled_rule_list_model.clear()
        self.remove_button.setEnabled(false)
        self.run_button.setEnabled(false)

    def handle_effects_of_rule(self,new_nodes,removed_nodes,replaced_nodes,new_edges,removed_edges,replaced_edges):

        #first add nodes, then edges, because edges can point to/from new node
        print "NewNodes:\n"
        for node in new_nodes:
            print "\t"+node.toString()+"\n"
            new_node=addNode(node.arg(1).value)
            fill_in_node(new_node,node)

        print "NewEdges:\n"
        for edge in new_edges:
            print "\t"+edge.toString()+"\n"
            new_edge=addDirectedEdge(edge.arg(1).value,edge.arg(2).value)
            fill_in_edge(new_edge,edge)

        print "ReplacedNodes:\n"
        for node in replaced_nodes:
            print "\t"+node.toString()+"\n"
            tmpList=(name==node.arg(1).value)
            if tmpList.size()>0:
                replaced_node=tmpList[0]
                fill_in_node(replaced_node,node)
            else:
                raise RuntimeError("The node I want to update does not exist anymore...")

        print "ReplacedEdges:\n"
        for edge in replaced_edges:
            print "\t"+edge.toString()+"\n"
            src=edge.arg(1).toString()
            dst=edge.arg(2).toString()
            timestamp=edge.arg(5).intValue()

            done=false
            tmp_list=((node1==src)&(node2==dst))
            for edgee in tmp_list:
                if edgee.tstamp==timestamp:
                    fill_in_edge(edgee,edge)
                    done=true
                    break

            if not(done):
                raise RuntimeError("Should have replaced an edge, but did NOT find the right one!")


        #first remove edges, then nodes (removing a node removes any edges pointing to/from it)
        print "RemovedEdges:\n"
        for edge in removed_edges:
            print "\t"+edge.toString()+"\n"
#            print "$$ "+edge.toString()+": "+edge.typeName()+" "+edge.name()+" "+"\n"
            src=edge.arg(1).toString()
            dst=edge.arg(2).toString()
#            print ">"+edge.arg(5).getClass().getName()+"\n"
            timestamp=edge.arg(5).intValue()
            print "-- "+src+" -> "+dst+"\n"
            done=false
            tmp_list=((node1==src)&(node2==dst))
            for edgee in tmp_list:
                if edgee.tstamp==timestamp:
                    removeEdge(edgee)
                    done=true
                    break

            if not(done):
                raise RuntimeError("Should have removed an edge, but did NOT find the right one!")
#            removed_edge=filter(lambda edgee: edgee.tstamp==timestamp,tmp_list)[0]

#            removeEdge(removed_edge)

        print "RemovedNodes:\n"
        for node in removed_nodes:
            print "\t"+node.toString()+" -> "+node.arg(1).toString()+"\n"

            tmpList=(name==(node.arg(1).toString().toString()))
            if tmpList.size()>0:
                removed_node=tmpList[0]
                removeNode(removed_node)
            else:
                raise RuntimeError("The node I should remove is already removed...")
    

        #offer chance to confirm (just query) or cancel (query and morph)
#        answer=JOptionPane.showInternalConfirmDialog(ui.getContentPane(),"Are you satisfied with this reduction?", "Are you happy?",JOptionPane.YES_NO_OPTION, JOptionPane.QUESTION_MESSAGE);

#        if answer == JOptionPane.YES_OPTION:
#            query="catch(confirm_ui_reduction,E,(print_message(error,E),fail))"
#            Query(query).oneSolution()        
#        else:
#            query="catch(cancel_ui_reduction,E,(print_message(error,E),fail))"
#            Query(query).oneSolution()
#            morph(start_state_name,50000)

    def hide_dialog(self):
        self.dialog.setVisible(false)
        self.dialog.dispose()

def yes_action(event):
    reduction_commando.hide_dialog()
    Query("catch(confirm_ui_reduction,E,(print_message(error,E),fail))").oneSolution()

    #recolor everything
    addBaseLegend(concerns)

def no_action(event):
    reduction_commando.hide_dialog()
    Query("catch(cancel_ui_reduction,E,(print_message(error,E),fail))").oneSolution()
    # does NOT work yet
    #    morph(reduction_commando.start_state_name,50000)
    ls(reduction_commando.start_state_name)

    #recolor everything
    addBaseLegend(concerns)
    
def fill_in_node(node,compound):
    node.localname=compound.arg(1).value
    node.makefile=compound.arg(2).value
    node.line=compound.arg(3).value
    node.style=compound.arg(4).value
    node.concern=compound.arg(5).value
    node.error=compound.arg(6).value
    node.tstamp=compound.arg(7).value
    node.phony=compound.arg(8).value
    node.dir=compound.arg(9).value
    node.base=compound.arg(10).value
    node.inuse=compound.arg(11).value    

def fill_in_edge(edge,compound):
    edge.directed=compound.arg(2).value
    edge.ismeta=compound.arg(3).value
    edge.tstamp=compound.arg(4).value
    edge.pruning=compound.arg(5).value
    edge.implicit=compound.arg(6).value
