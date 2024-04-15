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

from javax.swing.filechooser import FileFilter

class MyFileFilter (FileFilter):

    def __init__(self,extension_list):

	self.extensions=extension_list

    def accept(self,afile):

	extension = getExtension(afile)
	if extension != None and self.extensions.count(extension) > 0:
	    return true
	elif afile.isDirectory():
            return true
        else:
	    return false

    def getDescription(self):

	return concatenate_list_of_strings(self.extensions)


def getExtension(afile):

    ext = None
    file_name = afile.getName()
    index = String(file_name).lastIndexOf(String("."))
    
    if index > 0 and  index < String(file_name).length() - 1:
	ext = String(String(file_name).substring(index+1)).toLowerCase()
	
    return ext
