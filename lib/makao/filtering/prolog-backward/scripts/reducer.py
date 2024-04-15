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
from jpl import JPL

class reducer:

    def reduce(self,list_of_rules):

	self.readRule(list_of_rules)
        query="reduce('blabla.pl')"
        Query(String(query)).allSolutions()

    def __init__(self):

        JPL.setDefaultInitArgs(["pl", "-g", "true", "-nosignals"]);
#        reifier(0).reify()
        chooser = JFileChooser(makao_path+"filtering/prolog-backward/experiments")
        chooser.setDialogTitle(String("Please select the Prolog model of the current graph."))
        chooser.setFileFilter(MyFileFilter(["pl"]))
        chooser.setMultiSelectionEnabled(false)
        chooser.setFileSelectionMode(JFileChooser.FILES_ONLY)
        returnVal = chooser.showOpenDialog(None)
	    
        if returnVal == JFileChooser.APPROVE_OPTION:
            #read in the source
            file = chooser.getSelectedFile()
            temp="'"+file.getAbsolutePath()+"'"
                    
            query="consult([%s,%s])" % ("'"+makao_path+"filtering/prolog-backward/rules/make-logic.pl'",temp)
            Query(query).oneSolution()    
        else:
            raise RuntimeError("You did not select a valid Prolog file!")

        #caching
        query="base_cached"
        Query(query).oneSolution()    

    def readPrologFiles(self,list_of_prolog_files):

	if len(list_of_prolog_files) == 0:
	    chooser = JFileChooser(makao_path+"filtering/prolog-backward/rules")
	    chooser.setDialogTitle(String("Please select the directory where your Prolog files reside."))
	    chooser.setFileFilter(MyFileFilter(["pl"]))
	    chooser.setMultiSelectionEnabled(true)
	    chooser.setFileSelectionMode(JFileChooser.FILES_ONLY)
	    returnVal = chooser.showOpenDialog(None)
	    
	    if returnVal == JFileChooser.APPROVE_OPTION:
                #read in the source
		files = chooser.getSelectedFiles()
                temp="'"+makao_path+"filtering/prolog-backward/rules/main.pl'"
		for file in files:
                    print ">> "+file.getName()+"\n"
                    temp=temp+",'"+file.getAbsolutePath()+"'"
                    
                query="consult([%s])" % (temp)
                Query(query).oneSolution()
                
	    else:
		raise RuntimeError("You did not select a valid rules file!")
	else:
	    for file in list_of_prolog_files:
                temp=temp+",'"+makao_path+"filtering/prolog-backward/rules/"+file+".pl'"
                    
            query="consult([%s])" % (temp)
#                query="consult('%s')" % (makao_path+"rules/prolog/"+file+".pl")
            Query(query).oneSolution()

        query="rule(X,_,_)"
        aHashMap=Query(query).allSolutions()
        res=[]
        for entry in aHashMap:
            res.append(entry.get("X"))

        return res
	
