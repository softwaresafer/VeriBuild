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

class weaver:

    def __init__(self,advice_name,debug):

        self.advice_name=advice_name
	self.debug=debug

	chooser = JFileChooser(System.getProperty("MAKAO"));
	chooser.setDialogTitle(String("Please select the directory for the generated weaver script."))
#	chooser.setFileFilter(MyFileFilter(["xml"]))
	chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY)
	returnVal = chooser.showOpenDialog(None)

	if returnVal == JFileChooser.APPROVE_OPTION:
	    self.dir = chooser.getSelectedFile().getAbsolutePath()
	else:
	    raise RuntimeError("You did not select a valid directory!")

    #better: use index of command in command list instead of command itself?
    #suffix="BEFORE" or "AFTER"
    #increment=1 (after) or 0 (before)
    def weave(self,target_list,command_list,advice_list,suffix,increment):

	weave_output=[]
	unweave_output=[]
        separator="\t#"+self.advice_name+"-"+suffix+"\',\'\t"

        if self.debug:
            print "About to sort...\n"
	file_to_line_number_index_subindex_triple=self.sort_by_makefile(target_list,command_list)

	for file in file_to_line_number_index_subindex_triple.keys():
            if self.debug:
#		file2=String("/case"+String(file).substring(9))
		file2=file
		print "Starting to weave in ",file2," ...\n"
                
	    weave_output.append("  # "+file)
            weave_output.append("  $current_file=\""+file+"\";")
	    weave_output.append("""  $current_file=~s/^${dir_in}/${dir_out}/;
  tie @tie_file, "Tie::File", "$current_file" or die "Could not open ${current_file}...";
  if($debug){
    print STDOUT "Weaving into ${current_file}.\\n";
  }
  ${$file_counter_ref}++;
""")

	    unweave_output.append("  # "+file)
            unweave_output.append("  $current_file=\""+file+"\";")
	    unweave_output.append("""  $current_file=~s/^${dir_in}/${dir_out}/;
  tie @tie_file, "Tie::File", "$current_file" or die "Could not open ${current_file}...";
  if($debug){
    print STDOUT "Unweaving into ${current_file}.\\n";
  }
  ${$file_counter_ref}++;
""")

	    #following needed to take change of line numbers into account
	    skew=0
            duplicate_advice=[]
	    for linenr,index,subindex in file_to_line_number_index_subindex_triple[file]:
		advice=advice_list[index].splitlines()
                target=target_list[index]
		skew_delta=len(advice)

                if self.debug:
                    print "Logical weaving of command on line ",linenr,"...\n"
                advice.reverse()
                for ad in advice:
                    commands[target.name].insert(subindex,ad+"\t#"+self.advice_name+"-"+suffix)
                advice.reverse()

                if duplicate_advice.count((linenr,subindex))==0:
                    weave_output.append("  # line "+str(linenr))
                    weave_output.append("  splice(@tie_file,"+str(linenr+increment-1+skew)+",0,\'\t"+separator.join(advice)+"\t#"+self.advice_name+"-"+suffix+"\');")
                    weave_output.append("  ${$jp_counter_ref}++;")
                    weave_output.append("")

                    unweave_output.append("  # line "+str(linenr))
                    unweave_output.append("  splice(@tie_file,"+str(linenr+increment-1)+","+str(skew_delta)+");")
                    unweave_output.append("  ${$jp_counter_ref}++;")
                    unweave_output.append("")

                    duplicate_advice.append((linenr,subindex))
                    skew+=skew_delta

            weave_output.append("  untie @tie_file;")
            weave_output.append("")

            unweave_output.append("  untie @tie_file;")
            unweave_output.append("")


        if self.debug:
            print "Physical weaving...\n"
	file=open(self.dir+"/weave-"+self.advice_name+".pl", 'w')
	self.write_preamble(file)
	self.write_list(file,weave_output)
	self.write_interludium(file)
	self.write_list(file,unweave_output)
	self.write_epilogue(file)
	file.close()
        if self.debug:
            print "Done...\n"

	return


    def unweave(self,suffix):

        for key in commands.keys():
            newc=[]
            for command in commands[key]:
                if not command.endswith("#"+self.advice_name+"-"+suffix):
                    newc.append(command)

            commands[key]=newc

    
    #better: use index of command in command list instead of command itself?
    def weave_before(self,target_list,command_list,advice_list):

        self.weave(target_list,command_list,advice_list,"BEFORE",0)

        return 


    def unweave_before(self):

        self.unweave("BEFORE")


    #better: use index of command in command list instead of command itself?
    def weave_after(self,target_list,command_list,advice_list):

        self.weave(target_list,command_list,advice_list,"AFTER",1)

	return


    def unweave_after(self):

        self.unweave("AFTER")


    #better: use index of command in command list instead of command itself?
    def weave_around(self,target_list,command_list,before_advice_list,after_advice_list):

        suffix="AROUND"
        increment=0
	weave_output=[]
	unweave_output=[]
        separator="\t#"+self.advice_name+"-"+suffix+"\',\'\t"

        if self.debug:
            print "About to sort...\n"
	file_to_line_number_index_subindex_triple=self.sort_by_makefile(target_list,command_list)

	for file in file_to_line_number_index_subindex_triple.keys():
            if self.debug:
#		file2=String("/case"+String(file).substring(9))
		file2=file
		print "Starting to weave in ",file2," ...\n"
                
	    weave_output.append("  # "+file)
            weave_output.append("  $current_file=\""+file+"\";")
	    weave_output.append("""  $current_file=~s/^${dir_in}/${dir_out}/;
  tie @tie_file, "Tie::File", "$current_file" or die "Could not open ${current_file}...";
  if($debug){
    print STDOUT "Weaving into ${current_file}.\\n";
  }
  ${$file_counter_ref}++;
""")

	    unweave_output.append("  # "+file)
            unweave_output.append("  $current_file=\""+file+"\";")
	    unweave_output.append("""  $current_file=~s/^${dir_in}/${dir_out}/;
  tie @tie_file, "Tie::File", "$current_file" or die "Could not open ${current_file}...";
  if($debug){
    print STDOUT "Unweaving into ${current_file}.\\n";
  }
  ${$file_counter_ref}++;
""")

	    #following needed to take change of line numbers into account
	    skew=-1
            duplicate_advice=[]
	    for linenr,index,subindex in file_to_line_number_index_subindex_triple[file]:
		before_advice=before_advice_list[index].splitlines()
                target=target_list[index]
		skew_delta=len(before_advice)

                if self.debug:
                    print "Logical around weaving (before) of command on line ",linenr,"...\n"
                    if linenr==67:
                        print "value: ",(linenr+increment-1+skew),"\n"
                        print "incr: ",increment,"\n"
                        print "skew: ",skew,"\n"
                    if linenr==74:
                        print "value: ",(linenr+increment-1+skew),"\n"
                        print "incr: ",increment,"\n"
                        print "skew: ",skew,"\n"
                before_advice.reverse()
                for ad in before_advice:
                    commands[target.name].insert(subindex,ad+"\t#"+self.advice_name+"-"+suffix)
                before_advice.reverse()

                if duplicate_advice.count((linenr,subindex))==0:
                    weave_output.append("  # line "+str(linenr))
                    weave_output.append("  splice(@tie_file,"+str(linenr+increment-1+skew)+",0,\'\t"+separator.join(before_advice)+"\t#"+self.advice_name+"-"+suffix+"\');")
#                    weave_output.append("  ${$jp_counter_ref}++;")
                    weave_output.append("")

                    unweave_output.append("  # line "+str(linenr))
                    unweave_output.append("  splice(@tie_file,"+str(linenr+increment-2)+","+str(skew_delta)+");")
#                    unweave_output.append("  ${$jp_counter_ref}++;")
                    unweave_output.append("")

#                    duplicate_advice.append((linenr,subindex))
                    skew+=skew_delta
                    skew+=1 #join point itself

                new_subindex=subindex+skew_delta+1
                after_advice=after_advice_list[index].splitlines()
		skew_delta=len(after_advice)
                increment=1

                if self.debug:
                    print "Logical around weaving (after) of command on line ",linenr,"...\n"
                after_advice.reverse()
                for ad in after_advice:
                    commands[target.name].insert(new_subindex,ad+"\t#"+self.advice_name+"-"+suffix)
                after_advice.reverse()

                if duplicate_advice.count((linenr,subindex))==0:
                    weave_output.append("  # line "+str(linenr))
                    weave_output.append("  splice(@tie_file,"+str(linenr+increment-1+skew)+",0,\'\t"+separator.join(after_advice)+"\t#"+self.advice_name+"-"+suffix+"\');")
                    weave_output.append("  ${$jp_counter_ref}++;")
                    weave_output.append("")

                    unweave_output.append("  # line "+str(linenr))
                    unweave_output.append("  splice(@tie_file,"+str(linenr+increment-1)+","+str(skew_delta)+");")
                    unweave_output.append("  ${$jp_counter_ref}++;")
                    unweave_output.append("")

                    duplicate_advice.append((linenr,subindex))
                    skew+=skew_delta-1

            weave_output.append("  untie @tie_file;")
            weave_output.append("")

            unweave_output.append("  untie @tie_file;")
            unweave_output.append("")


        if self.debug:
            print "Physical weaving...\n"
	file=open(self.dir+"/weave-"+self.advice_name+".pl", 'w')
	self.write_preamble(file)
	self.write_list(file,weave_output)
	self.write_interludium(file)
	self.write_list(file,unweave_output)
	self.write_epilogue(file)
	file.close()
        if self.debug:
            print "Done...\n"

	return


    def unweave_around(self):

        self.unweave("AROUND")


    def write_preamble(self,file):

	file.write("""#!/usr/bin/perl

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
# The Original Code is MAKAO Weaver.
#
# The Initial Developer of the Original Code is
# Bram Adams (bramDOTadamsATugentDOTbe).
# Portions created by the Initial Developer are Copyright (C) 2006
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#
# ***** END LICENSE BLOCK *****

use strict;
use warnings;
use Getopt::Long;
use Tie::File;

# ===================================================================
# Process command line options...                                   =
# ===================================================================

my $current_version="1.8";

# Options...
my $help = 0;
my $version = 0;
my $quiet = 0;
my $action = '';
my $dir_in = '';
my $dir_out = '';
my $debug = 0;
#my $teller=0;

# Process command line options...
GetOptions (
  'help|?' => \$help,
  'version' => \$version,
  'quiet' => \$quiet,
  'debug' => \$debug,
  'action:s' => \$action,
  'in:s' => \$dir_in,
  'out:s' => \$dir_out,
) or usage_and_exit ();

# Show help if requested...
if ($help) { usage_and_exit (); }

# Show version info if requested...
if ($version) { version_and_exit (); }


# ===================================================================
# Check and perform right action                                    =
# ===================================================================

my $file_counter=0;
my $jp_counter=0;

if ($action eq "weave"){
  if($debug){
    print STDOUT "About to weave using ${dir_in} -> ${dir_out}...\\n";
  }
  weave(\$file_counter,\$jp_counter);
}elsif ($action eq "unweave"){
  if($debug){
    print STDOUT "About to unweave using ${dir_in} -> ${dir_out}...\\n";
  }
  unweave(\$file_counter,\$jp_counter);
}else{
  die "Action should \\"weave\\" or \\"unweave\\", but you provided \\"${action}\\"...";
}


# ===================================================================
# Endgame...                                                        =
# ===================================================================

if (!$quiet) {
  print STDOUT ("Processed:\\n\\t* ${file_counter} file(s);\\n\\t* ${jp_counter} join points(s).\\n");
}

exit(0);

# ===================================================================
# (Un)Weaving...                                                    =
# ===================================================================

sub weave {
  my ($file_counter_ref,$jp_counter_ref)=@_;
  my $current_file="";
  my @tie_file=();

""")

	return


    def write_interludium(self,file):

	file.write("""}

sub unweave {
  my ($file_counter_ref,$jp_counter_ref)=@_;
  my $current_file="";
  my @tie_file=();

""")

	return


    def write_epilogue(self,file):

	file.write("""}


# ===================================================================
# Utility methods...                                                =
# ===================================================================

sub contains_text {
    my ($token,$list_ref)=@_;

    foreach my $element (@{$list_ref}){
	if(defined($element) and ($element eq $token)){ return 1; }
    }

    return 0;
}

# ===================================================================
# Boilerplating for script...                                       =
# ===================================================================

sub usage_and_exit {
  print STDERR ("Usage: weaver.pl -action ACTION [OPTIONS]...\\n");
  print STDERR ("Where ACTION is one of:\\n");
  print STDERR ("  weave         weaving of advice in build system\\n");
  print STDERR ("  unweave       undo weaving of advice in build system\\n");
  print STDERR ("Where OPTIONS is one of:\\n");
  print STDERR ("  -in           path used during build\\n");
  print STDERR ("  -out          path used during physical weaving\\n");
  print STDERR ("  -debug        show debug info\\n");
  print STDERR ("  -quiet        no report at end of run\\n");
  print STDERR ("  -version      show version information\\n");
  print STDERR ("  -help         print this message\\n");
  print STDERR ("\\n");
  exit (0);
}

# ===================================================================

sub version_and_exit {
  print STDERR ("This is \\"weaver.pl\\", automatically generated by MAKAO Weaver ${current_version}.\\n");
  print STDERR ("Part of the MAKAO project.\\n");
  exit (0);
}
""")

	return


    def write_list(self,file,alist):

	for s in alist:
	    file.write(s+"\n")


    def sort_by_makefile(self,target_list,command_list):

	res={}
	index=0

	for target,command in zip(target_list,command_list):
	    if(not res.has_key(target.makefile)):
		res[target.makefile]=[]

#            print("Command: "+command+"\nTarget: "+target.name+"\n")
            subindex=commands[target.name].index(command)
            line=target.line+subindex
            line_index_subindex=line,index,subindex
	    res[target.makefile].append(line_index_subindex)
            index+=1

	for key in res.keys():
	    res[key].sort()

        return res
    
