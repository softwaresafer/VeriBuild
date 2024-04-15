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
#from java.lang import System

#Prefuse controls
class prefuse_actions:

    def __init__(self):

        self.view=prefuse_bar('Prefuse Actions')


class prefuse_bar(DockableAdapter):

    def __init__(self,new_title):

        self.atitle=new_title

        centerButton = JButton("CENTER")
        centerButton.setForeground(Color.RED)
        centerButton.actionPerformed = lambda event: v.center()
        self.add(centerButton)

        save_quitButton = JButton("SAVE & QUIT")
        save_quitButton.actionPerformed = lambda event: save_and_exit(gdf_dir_name+gdf_file_name.replace(".gdf", ""))
        self.add(save_quitButton)
        
        save_analyzeButton = JButton("SAVE & ANALYZE")
        save_analyzeButton.setForeground(Color.GREEN)
        save_analyzeButton.actionPerformed = lambda event: save_and_analyze(gdf_dir_name+gdf_file_name.replace(".gdf", ""))
        self.add(save_analyzeButton)

        self.revalidate()
        self.repaint()
        ui.dock(self)
      
    def getTitle(self):

        # define the title in the window
        return('%s' % self.atitle)
