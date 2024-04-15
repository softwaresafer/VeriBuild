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

from java.io import File
from java.io import FileReader
from javax.xml.stream import *
from javax.xml.stream.events import *
from javax.xml.namespace import QName

from javax.swing import JFileChooser

#Returns dictionary of node name to ordered array of commands
class xml_importer:

    def __init__(self,debug,work_dir):

	self.debug=debug

        print "[XML IMPORTED] ",gdf_dir_name+gdf_file_name+".xml\n";
        self.file = File(gdf_dir_name,gdf_file_name+".xml")#try normal location first
        if not(self.file.exists()):
            self.file = File(gdf_dir_name,gdf_file_name.replace("-piccolo", "")+".xml")#try normal location first for -piccolo graph
        if not(self.file.exists()):
            chooser = JFileChooser(work_dir);
            chooser.setDialogTitle(String("Please select the .xml file with appropriate target commands."))
            chooser.setFileFilter(MyFileFilter(["xml"]))
            returnVal = chooser.showOpenDialog(None)

            if returnVal == JFileChooser.APPROVE_OPTION:
                self.file = chooser.getSelectedFile()
            else:
                raise RuntimeError("You did not select a valid XML file!")


    def parse_file(self):
	
	factory = XMLInputFactory.newInstance()
        factory.setProperty(XMLInputFactory.IS_REPLACING_ENTITY_REFERENCES,Boolean("false"))
	reader = factory.createXMLEventReader(FileReader(self.file))

	result_dictionary = {}
	result_dictionary_actual = {}
        result_dictionary_macro = {}

	target = ""
	commands = []
        actuals_started=false
        macros_started=false

	while reader.hasNext():

	    event = reader.nextEvent()
	    event_type = event.getEventType()
	    nextEvent = reader.peek()

	    if event_type == XMLEvent.END_DOCUMENT:
		break
	    
	    elif event_type == XMLEvent.START_ELEMENT:		
		startElement = event.asStartElement()

		if String(startElement.getName().getLocalPart()).equals(String("build")):
		    continue
		elif String(startElement.getName().getLocalPart()).equals("target"):
		    target = startElement.getAttributeByName(QName("name")).getValue()
		    commands = []
		    if self.debug:
			print "ENTERED: ",target,"\n"
		elif String(startElement.getName().getLocalPart()).equals("command"):
                    command=""
                    while nextEvent.isCharacters() or nextEvent.isEntityReference():
                        if nextEvent.isCharacters():
                            command+=reader.nextEvent().asCharacters().getData()
                        elif nextEvent.isEntityReference():
                            command+=self.resolve_internal_entity_reference(reader.nextEvent().getName())
                        nextEvent = reader.peek()

                    commands.append(command)
                    if self.debug:
                        print "\tCOMMAND: ",command,"\n"
		elif String(startElement.getName().getLocalPart()).equals("actual_command"):
                    if not actuals_started:
                        result_dictionary[target] = commands
                        commands=[]
                        actuals_started=true

                    command=""
                    while nextEvent.isCharacters() or nextEvent.isEntityReference():
                        if nextEvent.isCharacters():
                            command+=reader.nextEvent().asCharacters().getData()
                        elif nextEvent.isEntityReference():
                            command+=self.resolve_internal_entity_reference(reader.nextEvent().getName())
                        nextEvent = reader.peek()

                    commands.append(command)
                    if self.debug:
                        print "\tACTUAL COMMAND: ",command,"\n"
		elif String(startElement.getName().getLocalPart()).equals("macro"):
                    if not macros_started:
                        result_dictionary_actual[target] = commands
                        commands=[]
                        macros_started=true

                    command=""
                    while nextEvent.isCharacters() or nextEvent.isEntityReference():
                        if nextEvent.isCharacters():
                            command+=reader.nextEvent().asCharacters().getData()
                        elif nextEvent.isEntityReference():
                            command+=self.resolve_internal_entity_reference(reader.nextEvent().getName())
                        nextEvent = reader.peek()

                    commands.append(command)
                    if self.debug:
                        print "\tMACRO: ",command,"\n"

	    elif event_type == XMLEvent.END_ELEMENT:
		endElement = event.asEndElement()

		if String(endElement.getName().getLocalPart()).equals("build"):
		    continue
		elif String(endElement.getName().getLocalPart()).equals("target"):
#		    possible_targets=(name==target)
#		    if len(possible_targets) == 0:
#			possible_targets=(name['_deleted']==target)
                    if macros_started == 1:
                        result_dictionary_macro[target] = commands
                    else:
                        result_dictionary_actual[target] = commands
                    actuals_started=false
                    macros_started=false
		    if self.debug:
			print "EXITED: ",target,"\n"
		elif String(endElement.getName().getLocalPart()).equals("command"):
		    continue
		elif String(endElement.getName().getLocalPart()).equals("actual_command"):
		    continue
		elif String(endElement.getName().getLocalPart()).equals("macro"):
		    continue

	reader.close()

	return [result_dictionary,result_dictionary_actual,result_dictionary_macro]

    def resolve_internal_entity_reference(self,entity):

        if String(entity).equals(String("lt")):
            return "<"
        elif String(entity).equals(String("gt")):
            return ">"
        elif String(entity).equals(String("quot")):
            return "\""
        elif String(entity).equals(String("amp")):
            return "&"
        elif String(entity).equals(String("apos")):
            return "\'"
        else:
            error_string="Unknown internal XML entity reference: <<"
            error_string+=entity
            error_string+=">>"
            raise RuntimeError(error_string)

