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

from javax.swing import JButton
from com.hp.hpl.guess.ui import DockableAdapter

class dockie(DockableAdapter):

      def __init__(self):
            DockableAdapter.__init__(self)

            # create a new button called center
            testButton = JButton("center")

            # every time the button is pressed, center the display
            testButton.actionPerformed = lambda event: v.center()

            # add the button to the toolbar
            self.add(testButton)

            # add the toolbar to the main UI window            
            ui.dock(self)

      def getTitle(self):

            # define the title in the window
            return("dockie") 
