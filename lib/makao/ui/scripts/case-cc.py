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

#1. Find join point shadows
jps=(concern=="c").inEdges.node1.findNodes()

#2. Gather context
context=[(command,tool,target) for target in jps
                               for command in commands[target.name]
                               for tool in ["(CC)","(CC_ISAM)","(CC_SIMPLE)","gcc"]
                               if command.find(tool)!=-1 ]

#3. Compose advice
before_advice=["\n".join([c.replace(t,t+" -E")+" -o p-${<}",
                        "mv ${<} ${<}-orig",
                        "aspicere.sh p-${<} ${<}"])
                           for (c,t,ta) in context                       ]

after_advice=["mv ${<}-orig ${<}"
                           for (c,t,ta) in context                       ]

print("Size of target_list:\t"+str(len(context)))
print("Size of advice_list:\t"+str(len(before_advice)))
print("Size of command_list:\t"+str(len(context)))

#4. Weave
cc_weaver=weaver("aspicere-cc",1)
cc_weaver.weave_around([ta for (c,to,ta) in context],[c for (c,to,ta) in context],before_advice,after_advice)