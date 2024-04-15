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

#######################
#######################
## Node context menu ##
#######################
#######################

# 1) Commands menu: show command list

# create a new menu item
commandMenuItem = NodeEditorPopup.addItem("Commands")

# define an action for that menu item
def commands_action(_target_list):

    for _target in _target_list:
#        print "The identity is ", id(_target)
#        print "Type is ", type(_target)
        print "Commands for <",_target.name,">: "
        pp(_target)
        print "--------"

# map the events produced by the click events to the action function
commandMenuItem.menuEvent = commands_action

######################################################################

# 2) Actual commands menu: show command list

# create a new menu item
actualCommandMenuItem = NodeEditorPopup.addItem("Actual Commands")

# define an action for that menu item
def actualCommands_action(_target_list):

    for _target in _target_list:
#        print "The identity is ", id(_target)
#        print "Type is ", type(_target)
        print "Actual commands for <",_target.name,">: "
        pp2(_target)
        print "--------"

# map the events produced by the click events to the action function
actualCommandMenuItem.menuEvent = actualCommands_action

######################################################################

# 2) Macros menu: show macro list

# create a new menu item
macroMenuItem = NodeEditorPopup.addItem("Active Macros")

# define an action for that menu item
def macros_action(_target_list):

    for _target in _target_list:
#        print "The identity is ", id(_target)
#        print "Type is ", type(_target)
        print "Active macros for <",_target.name,">: "
        pp3(_target)
        print "--------"

# map the events produced by the click events to the action function
macroMenuItem.menuEvent = macros_action

######################################################################

# 3) Whereabouts menu: show makefile and line number

# create a new menu item
whereMenuItem = NodeEditorPopup.addItem("Whereabouts")

# define an action for that menu item
def where_action(_target_list):

    for _target in _target_list:
#        print "The identity is ", id(_target)
#        print "Type is ", type(_target)
        print "Where: <",_target.name,"> in <",_target.makefile,">:<",_target.line,">"


# map the events produced by the click events to the action function
whereMenuItem.menuEvent = where_action

######################################################################

# 4) Hide menu: hide target

# create a new menu item
hideMenuItem = NodeEditorPopup.addItem("Hide")

# define an action for that menu item
def hide_action(_target_list):

    for _target in _target_list:
#        print "The identity is ", id(_target)
#        print "Type is ", type(_target)
         _target.visible=0


# map the events produced by the click events to the action function
hideMenuItem.menuEvent = hide_action


#######################
#######################
## Edge context menu ##
#######################
#######################

# 1) Time stamp menu: show time stamp

# create a new menu item
tstampMenuItem = EdgeEditorPopup.addItem("Time stamp")

# define an action for that menu item
def tstamp_action(_edge_list):

    for _edge in _edge_list:
#        print "The identity is ", id(_target)
#        print "Type is ", type(_target)
#         _target.visible=0
        print "When: <",_edge.node1.name,"> --> <",_edge.node2.name,">@<",_edge.tstamp,">"


# map the events produced by the click events to the action function
tstampMenuItem.menuEvent = tstamp_action

######################################################################

# 2) Status menu: show edge status

# create a new menu item
statusMenuItem = EdgeEditorPopup.addItem("Status")

# define an action for that menu item
def status_action(_edge_list):

    for _edge in _edge_list:
#        print "The identity is ", id(_target)
#        print "Type is ", type(_target)
#         _target.visible=0        
        print "Status: <",(_edge.ismeta and "META" or "BASE"),"> - <",(_edge.pruning and "PRUNING" or "PROCESSED"),"> - <",(_edge.implicit and "IMPLICIT" or "EXPLICIT"),">"

# map the events produced by the click events to the action function
statusMenuItem.menuEvent = status_action
