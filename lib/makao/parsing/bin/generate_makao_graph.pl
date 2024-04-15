#!/usr/bin/perl

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
#    Dieter Paeps
#    Reinier Post (http://www.win.tue.nl/~rp/)
#
# ***** END LICENSE BLOCK *****

use strict;
use warnings;
no warnings 'recursion';
use Getopt::Long;
use File::Basename;
use XML::Writer;

#use lib "$ENV{MAKAO}";
#require "Parser.pm";
#use Shell::Parser;

# ===================================================================
# Process command line options...                                   =
# ===================================================================

my $current_version="1.8";

# Options...
my $help = 0;
my $version = 0;
my $quiet = 0;
my $file_in = '';
my $file_out = '';
my $xml_out = '';
my $debug = 0;
my $debugperf = 0;
my $eightyone = 0;#support for GNU Make 3.81
my $eightytwo = 0;#support for GNU Make 3.82
my $four = 0;#support for GNU Make 4
my $back_quote = '';
my $format = "gdf";
my $unused = 0;
#my $build_dir = '';#directory from within which build is started
my @supported_formats=("gdf","vrmlgraph","ncol","prolog");
my $nr_of_make_processes_started=0;
my @current_dirs=();
my $current_dir_counter=0;
my $implicit_dep_counter=0;
my $unused_target_counter=0;

my $line_count = 0;
my $input = '';
my $last_input_did_match=1;#should only be used in consume*()-methods or with care
my $last_input_was_eof=0;#should only be used in consume*()-methods or with care

# Process command line options...
GetOptions (
  'help|?' => \$help,
  'version' => \$version,
  'quiet' => \$quiet,
  'debug' => \$debug,
  'debugperf' => \$debugperf,
  'in:s' => \$file_in,
  'out:s' => \$file_out,
  'xml:s' => \$xml_out,
  'format:s' => \$format,
  'unused' => \$unused
#  'dir:s' => \$build_dir
) or usage_and_exit ();

# Show help if requested...
if ($help) { usage_and_exit (); }

# Show version info if requested...
if ($version) { version_and_exit (); }


# ===================================================================
# Prepare I/O streams...                                            =
# ===================================================================
my $HANDLE_IN;
my $HANDLE_OUT;
my $HANDLE_XML;

my $make_shell="garbage_value_such_that_things_work_if_no_shell_defined";
my $explicit_shell_command_timer_running=0;

usage_and_exit () unless ($file_in and $file_out);


#my $nr_of_anomalous_make_processes=0;

# Prepare input stream...
if ($file_in) {
  open ($HANDLE_IN, $file_in) or die "Input file ${file_in} could not be found!";
  collect_current_dirs(\@current_dirs);#these are almost randomly spread over trace, so do a first iteration to collect them all at once!
  close($HANDLE_IN);

#  ($build_dir eq $current_dirs[$current_dir_counter]) or die "Wrong initial build directory.";

  open ($HANDLE_IN, $file_in) or die "Input file ${file_in} could not be found!";
}

# Prepare graph output stream...
if ($file_out) {
  open ($HANDLE_OUT, ">$file_out") or die "Graph output file ${file_out} could not be opened!";
}

# Prepare XML output stream...
if (! ${xml_out}) {
    $xml_out .= "${file_out}.xml";
}
open ($HANDLE_XML, ">$xml_out") or die "XML output file ${xml_out} could not be opened!";

# ===================================================================
# Main logic...                                                     =
# ===================================================================

my %edges=();#id->ref of (node1_id,node2_id)
my $edge_count = 0;

my $EDGES_SRC=0;
my $EDGES_DST=1;
my $EDGES_TYPE=2;
my $EDGES_TIME=3;
my $EDGES_PRUNING=4;
my $EDGES_IMPLICIT=5;
my $EDGES_RECURSIVE=6;

my %edges_src_to_dst=();#id->ref of ids

my %target_name_to_id=();#targetname -> id
my %targets=();#id->ref of (targetname,is_meta_dependency,error_code,makefile,line_number,commands_array_ref)
my %unused_targets=();#id->ref of (targetname,is_meta_dependency,error_code,makefile,line_number,commands_array_ref)
my $target_count = 0;

my $TARGETS_NAME=0;
my $TARGETS_META=1;
my $TARGETS_ERROR=2;
my $TARGETS_MAKEFILE=3;
my $TARGETS_LINE=4;
my $TARGETS_COMMANDS=5;
my $TARGETS_TIME=6;
my $TARGETS_PHONY=7;
my $TARGETS_DIRNAME=8;
my $TARGETS_BASENAME=9;
my $TARGETS_INUSE=10;
my $TARGETS_ACTUAL_COMMANDS=11;
my $TARGETS_MACROS=12;

my $dummy_target = "blablabla";
my $error=0;
my $node_edge_time=0;

my $busy_on_meta_level=0;#true when in cflow of read_makefiles (even if in base part of start_new_make_process in cflow); false otherwise

print STDOUT "Parsing ${file_in}...\n";
consume_banner() or die "Cannot parse the following input on line ${line_count}: ${input}, stopped";


my $writer = init_xml_file();

my $main_target=start_new_make_process($dummy_target) or die "Something went horribly wrong on line ${line_count}: ${input}, stopped";
close ($HANDLE_IN);

#if(consume("\\s*Re\-executing:\\s+make.*")){
#  die "Sorry, this is a strange build: there are actually two builds in this single trace. The second build starts on line ${line_count}. Please try to split the file, or mail MAKAO's author to integrate a \"merge two builds in a trace into the same graph\"-feature."
#}

my $nr_of_dirs=@current_dirs;
#print STDOUT "*** ${nr_of_make_processes_started}\n";
#print STDOUT "*** ${nr_of_dirs}\n";
#print STDOUT "*** ${nr_of_anomalous_make_processes}\n";
(${nr_of_make_processes_started} == ${nr_of_dirs}) or die "Error with detection of current dirs...";
#resolve_duplicates();

my %unused_name_to_id=();

if($format eq "gdf"){
    print STDOUT "Generating ${file_out}:\n";

    print STDOUT "\t* writing targets:\t";
    write_gdf_targets($main_target,\%unused_name_to_id);
    print STDOUT "OK\n";

    print STDOUT "\t* writing edges:\t";
    write_gdf_edges();
    print STDOUT "OK\n";

    print STDOUT "\t* writing XML data:\t";
    write_xml_data($main_target,\%unused_name_to_id,$writer);
    print STDOUT "OK\n";
}elsif($format eq "vrmlgraph"){
    #http://vrmlgraph.i-scream.org.uk/
    print STDOUT "Generating ${file_out}:\n";

    print STDOUT "\t* writing edges:\t";
    write_vrmlgraph_edges();
    print STDOUT "OK\n";

    print STDOUT "\t* writing XML data:\t";
    write_xml_data($main_target,\%unused_name_to_id,$writer);
    print STDOUT "OK\n";
}elsif($format eq "ncol"){
    #http://apropos.icmb.utexas.edu/lgl/
    print STDOUT "Generating ${file_out}:\n";

    print STDOUT "\t* writing edges:\t";
    write_ncol_edges();
    print STDOUT "OK\n";

    print STDOUT "\t* writing XML data:\t";
    write_xml_data($main_target,\%unused_name_to_id,$writer);
    print STDOUT "OK\n";
}elsif($format eq "prolog"){
    print STDOUT "Generating prolog file <${file_out}>...\n";

    print STDOUT "\t* writing targets and edges:\t";
    write_prolog ($main_target);
    print STDOUT "OK\n";

    print STDOUT "\t* writing XML data:\t";
    write_xml_data_for_prolog($main_target,\%unused_name_to_id,$writer);
    print STDOUT "OK\n";	
}else{
  my $tmp=join(">, <",@supported_formats);
  print STDERR "Cannot generate file with output format <${format}>. Please try one of the following output formats: <${tmp}>.\n";
}

close ($HANDLE_OUT);
close ($HANDLE_XML);

# ===================================================================
# Endgame...                                                        =
# ===================================================================

if (!$quiet) {
    my $implicit=$implicit_dep_counter;#number of new implicit dependencies
    my $explicit=$edge_count-$implicit;

    print STDOUT ("Processed:\n\t* ${line_count} line(s);\n\t* ${explicit} explicit edge(s);\n\t* ${implicit} implicit edge(s);\n\t* ${target_count} target(s)");
    if($unused){
	print STDOUT (";\n\t* ${unused_target_counter} unused target(s).\n");
    }else{
	print STDOUT (".\n");
    }
}

exit(0);


# ===================================================================
# Consume utility methods...                                        =
# ===================================================================

sub consume {
    my ($string)=@_;

    if($last_input_did_match){
      $last_input_was_eof=eof($HANDLE_IN);

      if($last_input_was_eof){#currently EOF?
	return 0;
      }else{
	$input=<$HANDLE_IN>;
	$line_count++;
	
	while(($input =~ /^\s*$/)&&!$last_input_was_eof){#skip whitespace-lines
	  $last_input_was_eof=eof($HANDLE_IN);
	  
	  if($last_input_was_eof){#currently EOF?
	    return 0;
	  }else{
	    $input=<$HANDLE_IN>;
	    $line_count++;
	  }
	}

	chomp($input);

	if($debug){
	  print STDOUT "${line_count}:\t${input} tries ${string}\n";
	}

	$last_input_did_match=($input =~ $string);

	return $last_input_did_match;
      }
    }else{
      if($last_input_was_eof){#currently EOF?
	return 0;
      }else{
	if($debug){
	  print STDOUT "${line_count}:\t${input} retries ${string}\n";
	}
	$last_input_did_match=($input =~ $string);
	return $last_input_did_match;
      }
    }
}

sub consume_and_capture {
    my ($string,$captures_ref)=@_;

    if($last_input_did_match){
      $last_input_was_eof=eof($HANDLE_IN);

      if($last_input_was_eof){#currently EOF?
	return 0;
      }else{
	$input=<$HANDLE_IN>;
	$line_count++;
	
	while(($input =~ /^\s*$/)&&!$last_input_was_eof){#skip whitespace-lines
	  $last_input_was_eof=eof($HANDLE_IN);
	  
	  if($last_input_was_eof){#currently EOF?
	    return 0;
	  }else{
	    $input=<$HANDLE_IN>;
	    $line_count++;
	  }
	}

	chomp($input);

	if($debug){
	  print STDOUT "${line_count}:\t${input} tries ${string}\n";
	}

	$last_input_did_match=($input =~ $string);

	if($last_input_did_match){
 	  my @stringarray=split(//,$input);
	
	  for(my $index=1;$index<(@-) && $index<(@+);$index++){
	    my $tmp=join("",@stringarray[$-[$index] .. $+[$index]-1]);
	    push(@{$captures_ref},$tmp);
	  }
	}

	return $last_input_did_match;
      }
    }else{
      if($last_input_was_eof){#currently EOF?
	return 0;
      }else{
	$last_input_did_match=($input =~ $string);

	if($debug){
	  print STDOUT "${line_count}:\t${input} retries ${string}\n";
	}

	if($last_input_did_match){
	  my @stringarray=split(//,$input);
	
	  for(my $index=1;$index<(@-) && $index<(@+);$index++){
	    my $tmp=join("",@stringarray[$-[$index] .. $+[$index]-1]);
	    push(@{$captures_ref},$tmp);
	  }
	}

	return $last_input_did_match;
      }
    }
}

sub consume_banner {
    if(!consume("\\s*# GNU Make .\\...?.*")){ return 0; }

    if($input =~ m/3\.81\s*$/){
      $eightyone=1;
      $back_quote="`";
#      $eightytwo=0;
      if($debug){
	print STDOUT "Detected GNU Make 3.81.\n";
      }
    }elsif($input =~ m/3\.82\s*$/){
 #     $eightyone=0;
      $eightytwo=1;
      $back_quote="`";
      if($debug){
	print STDOUT "Detected GNU Make 3.82.\n";
      }
    }elsif($input =~ m/4\.0\s*$/){
      $four=1;
      $back_quote="'";
#      $four=1;
      if($debug){
	print STDOUT "Detected GNU Make 4.0.\n";
      }
    }else{
      $back_quote="`";
      if($debug){
	print STDOUT "Detected GNU Make <=3.80.\n";
      }
    }

    if(($eightytwo or $four) and !consume("\\s*# Built for .*")){ return 0; }
    if(!consume("\\s*# Copyright .*")){ return 0; }
    if(($eightytwo or $four) and !consume("\\s*# License GPLv3.*")){ return 0; }
    if(!consume("\\s*# This is free .*")){ return 0; }
    if(!consume("\\s*# There is NO .*")){ return 0; }
    if(!($eightytwo or $four) and !consume("\\s*# PARTICULAR PURPOSE\\..*")){ return 0; }
    if($eightyone and !consume("\\s*# This program built for .*")){ return 0; }


    return 1;
}

# ===================================================================
# Current directory fetching...                                     =
# ===================================================================

# Look out for cases where there is no entering/leaving info for a started make process. These processes get the previous current directory as their directory.
sub collect_current_dirs {
    my ($current_dirs_ref)=@_;

    my @stack=();
    my $entered_new_make_process=0;
#    my $nr_of_make_processes_without_entering_or_leaving_info=0;
    my $buffer_under_run=0;#check whether script contains more than one build (stack gets empty and is filled again)

    my $found_shell=0;

    print STDOUT "Scanning through ${file_in}...\n";

    while(consume(".*")){
      if($input =~ /#\s*(?:M|m)ake(?:\[.*\])?: Entering directory ${back_quote}(.*)'.*/){
	($buffer_under_run == 0) or die "Parsing ${file_in}...\nSorry, this is a strange build: there are actually two builds in this single trace, because one of the files included in the makefile were modified or created during the build. The second (actual) build starts after line ${buffer_under_run}.\n\nPlease try to split the file.";

	my @stringarray=split(//,$input);
	my $index=(@-)-1;
	#	    print STDOUT "${index} -> @{-}\n";
	#	    print STDOUT "${index} -> @{+}\n";
	my $dir_name=join("",@stringarray[$-[$index] .. $+[$index]-1]);
	$dir_name =~ s/'//g;
	$dir_name =~ s/`//g;
	push(@stack,$dir_name);
	push(@{$current_dirs_ref},$dir_name);

	$entered_new_make_process=0;
      }elsif($input =~ /\s*# (?:M|m)ake(?:\[.*\])?: Leaving directory ${back_quote}(.*)'.*/){
	if($entered_new_make_process){
	  #no entering/leaving info for previous make process(anomaly in e.g. linux-2.6.18-bzImage), so assume that it has same current directory as now on top of the stack
#	  $nr_of_make_processes_without_entering_or_leaving_info=$nr_of_make_processes_without_entering_or_leaving_info+1;

	  my $top_of_stack=$stack[$#stack];
	  push(@{$current_dirs_ref},$top_of_stack);;#do NOT push on stack => regular stack check not disturbed

	  $entered_new_make_process=0;
	}

	my @stringarray=split(//,$input);
	my $index=(@-)-1;
	my $dir_name=join("",@stringarray[$-[$index] .. $+[$index]-1]);
	$dir_name =~ s/'//g;
	$dir_name =~ s/`//g;
	my $check=pop(@stack);
	($check eq $dir_name) or die "Error during collection of current directory names: <${check}> vs. <${dir_name}>!";

	if(@stack == 0){
	  $buffer_under_run=$line_count;
	}
#      }elsif(($input =~ /\s*# GNU Make .\....*/) and consume("\\s*# Copyright .*") and consume("\\s*# This is free .*") and consume("\\s*# There is NO .*") and consume("\\s*# PARTICULAR PURPOSE\\..*")){
      }elsif(consume_banner()){
	if($entered_new_make_process){
	  #no entering/leaving info (anomaly in e.g. linux-2.6.18-bzImage), so assume that previous make process has same current directory as now on top of the stack
#	  $nr_of_make_processes_without_entering_or_leaving_info=$nr_of_make_processes_without_entering_or_leaving_info+1;

	  my $top_of_stack=$stack[$#stack];
	  push(@{$current_dirs_ref},$top_of_stack);#do NOT push on stack => regular stack check not disturbed
	}else{
	  $entered_new_make_process=1;
	}
      }elsif(not($found_shell) and ($input =~ m/^SHELL\s+:=\s+(.*)$/)){
	$make_shell=$1;
	if($debug){
	  print STDERR "SHELL: ${make_shell}\n";
	}
	$found_shell=1;
      }
    }

    my $nr_of_stack_elements=@stack;
    ($nr_of_stack_elements==0) or die "Error during collection of current directory names: remaining names on stack!";

    $line_count = 0;#reset counter
    $last_input_did_match=1;#reset
    $last_input_was_eof=0;#reset

#    return $nr_of_make_processes_without_entering_or_leaving_info;
}

# ===================================================================
# Various states...                                                 =
# ===================================================================

sub start_new_make_process {
    my ($parent_target)=@_;
    my @makefiles = ();

    my $current_dir=$current_dirs[$current_dir_counter];
    $current_dir_counter=$current_dir_counter+1;

    $nr_of_make_processes_started=$nr_of_make_processes_started+1;

    my %subtargetsnametoid=();#keep track of current dependencies
#    my $current_dir="";
#    print STDOUT "${line_count}: +++++++++++++++++++\n";

    my @top_level_targets=();
    my $new_target=$dummy_target;
    my $new_target_name=$dummy_target;

    my $only_meta_targets=read_makefiles(\@makefiles,\%subtargetsnametoid,$parent_target,$current_dir);
    if($only_meta_targets==0){
	die "This build log seems to be generated by GNU Make 3.81, but somehow the log says something different. Reading of makefiles did not succeed on line ${line_count}: ${input}, stopped";
    }elsif($only_meta_targets==2){
	if($debug){ print STDOUT "Gathered data:\n\t* makefiles: @{makefiles}\n"; }
    }else{
	if($debug){ print STDOUT "Gathered data:\n\t* makefiles: @{makefiles}\n"; }

	my @captures=();

	consume_and_capture("\\s*Considering target file ${back_quote}(.*)'.*",\@captures) or consume_and_capture("\\s*Pruning file ${back_quote}(.*)'.*",\@captures);
	$new_target_name=$captures[0];
	$new_target=register_target_and_edge($parent_target,$new_target_name,$current_dir,\%subtargetsnametoid,\@makefiles,(($input =~ /\s*Pruning.*/)?1:0),0,1);

	if($parent_target eq $dummy_target){
#	    $new_target=register_target($captures[0],\%subtargetsnametoid,\@makefiles,$current_dir);

	    #first process:
	    #a) make id of original target equal to name of target
	    my $tmp=delete($targets{$new_target});
	    my $old_name=$new_target;
	    $new_target=$captures[0];
	    $subtargetsnametoid{$new_target}=$new_target;
	    $targets{$new_target}=$tmp;
	    my $full_target_name=resolve_target_name($new_target,$current_dir);
	    $target_name_to_id{$full_target_name}=$new_target;
	    
	    #b)let original target depend on meta-dependencies and eliminate identity edges (node N -> node N)
	    for my $key (keys(%edges)){
		my ($src,$dst)=@{$edges{$key}};
		if($src eq $dummy_target){
		    if($dst eq $old_name){
		      #problem: edge from node N to itself (N)
		      delete($edges{$key});
		    }else{
		      $edges{$key}->[$EDGES_SRC]=$new_target;
		    }
		}
	    }
	}#else{	   
	 #   $new_target=register_target($captures[0],\%subtargetsnametoid,\@makefiles,$current_dir);
	 #   register_edge($parent_target,$new_target);
	#}
	
	if($input =~ /\s*Considering target file ${back_quote}\Q${new_target_name}\E'.*/){
	    start_new_target($new_target,\@makefiles,0,\%subtargetsnametoid,$current_dir,$new_target_name) or die "Starting new target did not succeed on line ${line_count}: ${input}, stopped";
	    
	    if($input =~ /\s*Giving up on target file ${back_quote}\Q${new_target_name}\E'.*/){
		consume("\\s*(?:M|m)ake(?:\\[.*\\])?: Target ${back_quote}\Q${new_target_name}\E' not remade because of errors.*") or die "Expected that target ${new_target_name} should not be remade because of errors on line ${line_count}, but found: ${input}\n";
	    }
	}elsif($input =~ /\s*Pruning file ${back_quote}\Q${new_target_name}\E'.*/){
	    my @captures=();
	    if(consume_and_capture("#\\s*(?:M|m)ake(?:\\[.*\\])?: Entering directory ${back_quote}(.*)'.*",\@captures)){
		($current_dir eq $captures[$#captures]) or die "Problem with current directory!";
		if($debug){ print STDOUT "ENTERED ${current_dir} on line ${line_count}\n"; }
	    }
	    consume("\\s*(?:M|m)ake(?:\\[.*\\])?: ${back_quote}\Q${new_target_name}\E' is up to date.*");
	}else{
	    return 0;
	}

        #Linux 2.6.x kernel
        if(consume("\\s*Removing intermediate files.*")){
	    while(consume("\\s*rm\\s+.*")){};
	}elsif(consume("\\s*(?:M|m)ake(?:\\[.*\\])?: ${back_quote}\Q${new_target_name}\E' is up to date.*")){}

	#Antlr-2.7.6
	push(@top_level_targets,$new_target_name);
	until(consume("\\s*# Make data base, printed on.*")){
	    @captures=();
	    consume_and_capture("\\s*Considering target file ${back_quote}(.*)'.*",\@captures) or consume_and_capture("\\s*Pruning file ${back_quote}(.*)'.*",\@captures) or consume("\\s*(?:M|m)ake(?:\\[.*\\])?: Nothing to be done for ${back_quote}\Q${new_target_name}\E'.*") or die "Expected another top-level target on line ${line_count}, but found: ${input}\n";
	    if($input =~ /\s*Pruning.*/){
	      register_target_and_edge($parent_target,$captures[0],$current_dir,\%subtargetsnametoid,\@makefiles,1,0,0);

	      #Firefox hack
	      consume("#\\s*(?:M|m)ake(?:\\[.*\\])?: Entering directory ${back_quote}.*'.*");
	    }elsif($input =~ /.*othing to be done.*/){
		#do nothing
	    }else{
	      if(contains_text($captures[0],\@top_level_targets)){
		#already registered
		$new_target=$subtargetsnametoid{$captures[0]};
	      }else{
		push(@top_level_targets,$captures[0]);
		#		$new_target=register_target($captures[0],\%subtargetsnametoid,\@makefiles,$current_dir);
		#		register_edge($parent_target,$new_target);
		$new_target=register_target_and_edge($parent_target,$captures[0],$current_dir,\%subtargetsnametoid,\@makefiles,0,0,0);
	      }
	      start_new_target($new_target,\@makefiles,0,\%subtargetsnametoid,$current_dir,$captures[0]) or die "Starting new target did not succeed on line ${line_count}: ${input}, stopped";
	      
	      if($input =~ /\s*Giving up on target file ${back_quote}\Q${new_target_name}\E'.*/){
		consume("\\s*(?:M|m)ake(?:\\[.*\\])?: Target ${back_quote}\Q${new_target_name}\E' not remade because of errors.*") or die "Expected that target ${new_target_name} should not be remade because of errors on line ${line_count}, but found: ${input}\n";
	      }elsif(consume("\\s*Removing intermediate files.*")){#Linux 2.6.x kernel
                while(consume("\\s*rm\\s+.*")){};
	      }
	    }
	}
    }

    enter_database($parent_target,\@makefiles,\%subtargetsnametoid,$current_dir) or die "Make database inventory did not succeed on line ${line_count}: ${input}, stopped";

    #update makefile-field with current_directory info
    for my $key (keys(%subtargetsnametoid)){
      my $id=$subtargetsnametoid{$key};
      if($targets{$id}->[$TARGETS_MAKEFILE] =~ /^\Q${current_dir}\E(.*)$/){
	  $targets{$id}->[$TARGETS_MAKEFILE] = "${current_dir}/";
      }else{
	my $makefile=${targets{$id}->[$TARGETS_MAKEFILE]};
	
	if($makefile eq "N/A"){
	  $targets{$id}->[$TARGETS_MAKEFILE] = "${current_dir}/";
	}else{
	  $targets{$id}->[$TARGETS_MAKEFILE] = "${current_dir}/${makefile}";
	}
      }	
    }
    

    if($debug){ print STDOUT "EXITED ${current_dir} on line ${line_count}\n"; }
    #print STDOUT "${line_count}: -----------------------\n";
    return $new_target;
}

sub read_makefiles {
    my ($makefiles_ref,$subtargetsnametoid_ref,$parent_target,$current_dir)=@_;
    if(!consume("\\s*Reading makefiles.*")){ return 0; }

    #update $busy_on_meta_level
    my $was_busy_on_meta_level=$busy_on_meta_level;
    if(not $was_busy_on_meta_level){
      $busy_on_meta_level=1;
    }
    
    while(consume("\\s*make\\s*\\[.+\\]\\s*:\\s+.*list too long.*")){}

    my @captures=();
    while(consume_and_capture("\\s*Reading makefile ${back_quote}(\\S*)'.*",\@captures)){
	push(@{$makefiles_ref},$captures[0]);
	@captures=();

	consume("^Checking build tools versions...");#Android hack
	if(consume("^\\s*(?:M|m)ake(?:\\[.*\\])?:\\s+\\/bin\\/bash -c: [cC]ommand not found")){ #Firefox hack
	  consume("#\\s*(?:M|m)ake(?:\\[.*\\])?: Entering directory ${back_quote}.*'.*");
	}elsif(consume_and_capture("#\\s*(?:M|m)ake(?:\\[.*\\])?: Entering directory ${back_quote}(.*)'.*",\@captures)){
	    ($current_dir eq $captures[$#captures]) or die "Problem with current directory!";
	    if($debug){ print STDOUT "ENTERED ${current_dir} on line ${line_count}\n"; }

	    #See tpico-all.txt on line 135
	    while(consume("^Makefile:\\d+: warning: ")){}#Qt hack
	    consume("^Makefile:\\d+:.*No such file or directory");
	}
	
	#avoid timing information of immediate variable execution:
	#Reading makefile ${back_quote}Makefile'...
	#+ uname
	#0.00user 0.00system 0:00.00elapsed 100%CPU (0avgtext+0avgdata 1933312maxresident)k
	#0inputs+1outputs (0major+403minor)pagefaults 0swaps
	#Updating makefiles....
	while(consume("^(\\+)+\\s+.*") or consume("^([0-9][\\.:0-9]+)user\\s+([0-9][\\.:0-9]+)system\\s+([0-9][\\.:0-9]+)elapsed") or consume("^([0-9]+)inputs\\s*\\+\\s*([0-9]+)outputs\\s+\\(([0-9]+)major\\s*\\+([0-9]+)minor\\)pagefaults\\s+([0-9]+)swaps") or consume("^diff: .*[nN]o such file or directory")){}

	#warning during immediate variable execution
	while(consume("\\s*make\\s*\\[.+\\]\\s*:\\s+.*list too long.*")){}

	#output during immediate variable execution
	if(consume("^===================================")){
	    #Android hack
	    do{
		consume(".*");
	    }until($input =~ m/^===================================/);
	}
    }

#    @captures=();
#    if(consume_and_capture("#\\s*(?:M|m)ake(?:\\[.*\\])?: Entering directory ${back_quote}(.*)'.*",\@captures)){
#	#See tpico-all.txt on line 135
#
#	($current_dir eq $captures[$#captures]) or die "Problem with current directory!";
#	if($debug){ print STDOUT "ENTERED ${current_dir} on line ${line_count}\n"; }
#
#	while(consume("^Makefile:\\d+: warning: ")){}#Qt hack
#	consume("^Makefile:\\d+:.*No such file or directory");
#    }

    if(!(consume("\\s*Updating makefiles.*"))){return 0;}

    #Firefox hack
    consume("^\\s*[mM]akefile ${back_quote}.*' might loop; not remaking it");

    my $res=update_makefiles($makefiles_ref,$subtargetsnametoid_ref,$parent_target,$current_dir) or die "Updating of makefiles did not succeed on line ${line_count}: ${input}";

    #update $busy_on_meta_level
    if(not $was_busy_on_meta_level){
      $busy_on_meta_level=0;
    }
    
    return $res;
}

sub update_makefiles {
    my ($makefiles_ref,$subtargetsnametoid_ref,$parent_target,$current_dir)=@_;

    my @captures=();
    while(consume_and_capture("\\s*Considering target file ${back_quote}(.*)'.*",\@captures) or consume_and_capture("\\s*Pruning file ${back_quote}(.*)'.*",\@captures)){
	if(!contains_text($captures[0],$makefiles_ref)){
	  push(@{$makefiles_ref},$captures[0]);
	}

#	my $new_target=register_target($captures[0],$subtargetsnametoid_ref,$makefiles_ref,$current_dir);
#	register_edge($parent_target,$new_target);
	my $new_target=register_target_and_edge($parent_target,$captures[0],$current_dir,$subtargetsnametoid_ref,$makefiles_ref,(($input =~ /\s*Pruning.*/)?1:0),0,0);

	#consider_makefiles($captures[0],$makefiles_ref,$subtargetsnametoid_ref);
	if($input =~ /\s*Considering.*/){#not needed when pruning
	    start_new_target($new_target,$makefiles_ref,1,$subtargetsnametoid_ref,$current_dir,$captures[0]);
	}

	@captures=();
    }

    if(consume("\\s*Updating goal targets.*")){
	return 1; 
    }elsif(consume("\\s*# Make data base, printed on.*")){
	return 2;
    }else{
	return 0;
    }
}

sub start_new_target {
    my ($parent_target,$makefiles_ref,$this_is_meta_target,$subtargetsnametoid_ref,$current_dir,$parent_target_name)=@_;
#    my $parent_target_name=$targets{$parent_target}->[$TARGETS_NAME];
    #my $t=$teller++;
    #print STDOUT "On ${line_count}: ${parent_target_name}/${parent_target}\n";

    my $db_entered=0;

    my @captures=();#has id's

#    until(${error} or consume("\\s*Finished prerequisites of target file ${back_quote}\Q${parent_target_name}\E'.*") or consume("\\s*File ${back_quote}\Q${parent_target_name}\E' was considered already.*")){
    until(${error} or consume("\\s*Finished prerequisites of target file ${back_quote}\Q${parent_target_name}\E'.*")){
      if(consume_and_capture("\\s*Considering target file ${back_quote}(.*)'.*",\@captures)){
	if($this_is_meta_target and !contains_text($captures[0],$makefiles_ref)){
	  push(@{$makefiles_ref},$captures[0]);
	}

#	my $new_target=register_target($captures[0],$subtargetsnametoid_ref,$makefiles_ref,$current_dir);
#	register_edge($parent_target,$new_target);
	my $new_target=register_target_and_edge($parent_target,$captures[0],$current_dir,$subtargetsnametoid_ref,$makefiles_ref,0,0,0);
	unless(consume("\\s*File ${back_quote}.*' was considered already.*")){
	  start_new_target($new_target,$makefiles_ref,$this_is_meta_target,$subtargetsnametoid_ref,$current_dir,$captures[0]);
	}
      }elsif(consume("\\s*File ${back_quote}\Q${parent_target_name}\E' does not exist.*")){
	#do not care
      }elsif(consume_and_capture("\\s*Pruning file ${back_quote}(.*)'.*",\@captures)){
	if($this_is_meta_target and !contains_text($captures[0],$makefiles_ref)){
	  push(@{$makefiles_ref},$captures[0]);
	}

#	my $new_target=register_target($captures[0],$subtargetsnametoid_ref,$makefiles_ref,$current_dir);
#	register_edge($parent_target,$new_target);
	my $new_target=register_target_and_edge($parent_target,$captures[0],$current_dir,$subtargetsnametoid_ref,$makefiles_ref,1,0,0);
      }elsif(consume("#\\s*(?:M|m)ake(?:\\[.*\\])?: Entering directory ${back_quote}(.*)'.*")){
	if(consume_and_capture("\\s*(?:M|m)ake(?:\\[.*\\])?: Circular (\\S+) <- (\\S+) dependency dropped\\.",\@captures)){
	    if($debug){
		print STDERR "CIRCULAR DEPENDENCY detected: <${input}>\n";
	    }
	    (($captures[0] eq $captures[1]) and ($captures[0] eq $parent_target_name)) or die "Incorrect circular dependency: ${input} <--> ${parent_target_name}";
	    my $edge=register_edge($parent_target,$parent_target,0);
	    $edges{$edge}->[$EDGES_PRUNING]=1;
	    $edges{$edge}->[$EDGES_RECURSIVE]=0;
	}else{
	  die("Encountered following line during search for prerequisites of ${parent_target_name} on line ${line_count}: ${input}, stopped");
	}
      }elsif(consume_and_capture("\\s*(?:M|m)ake(?:\\[.*\\])?: Circular (\\S+) <- (\\S+) dependency dropped\\.",\@captures)){
	    if($debug){
		print STDERR "CIRCULAR DEPENDENCY detected: <${input}>\n";
	    }
	    (($captures[0] eq $captures[1]) and ($captures[0] eq $parent_target_name)) or die "Incorrect circular dependency: ${input} <--> ${parent_target_name}";
	    my $edge=register_edge($parent_target,$parent_target,0);
	    $edges{$edge}->[$EDGES_PRUNING]=1;
	    $edges{$edge}->[$EDGES_RECURSIVE]=0;
      }else{
	die("Encountered following line during search for prerequisites of ${parent_target_name} on line ${line_count}: ${input}, stopped");
      }

      @captures=();
    }

    if($error){
	$targets{$subtargetsnametoid_ref->{$parent_target_name}}->[$TARGETS_ERROR]=$error;
    }

    unless($error or $input =~ /\s*File ${back_quote}\Q${parent_target_name}\E' was considered already.*/ or consume("\\s*Giving up on target file ${back_quote}\Q${parent_target_name}\E'.*")){
	decide_about_exec($parent_target,$makefiles_ref,$current_dir,$subtargetsnametoid_ref,$parent_target_name) or die "Decision about execution of target ${parent_target_name} does not succeed on line ${line_count}: ${input}, stopped";
    }

    #print STDOUT "UIT${t} on ${line_count}: ${parent_target_name}\n";
    return 1;
}

sub decide_about_exec {
    my ($parent_target,$makefiles_ref,$current_dir,$subtargetsnametoid_ref,$parent_target_name)=@_;
#    my $parent_target_name=$targets{$parent_target}->[$TARGETS_NAME]; error, because relative name can differ between various places

    if(consume("\\s*No (commands|recipe) for ${back_quote}\Q${parent_target_name}\E' and no prerequisites actually changed.*")){
      if(!consume("\\s*No need to remake target ${back_quote}\Q${parent_target_name}\E'.*")){ return 0; }
      if($input =~ /.*using VPATH name ${back_quote}(.*)'.*/){
	  $subtargetsnametoid_ref->{$1}=$subtargetsnametoid_ref->{$parent_target_name};
      }
    }elsif(consume("\\s*No need to remake target ${back_quote}\Q${parent_target_name}\E'.*")){
	if($input =~ /.*using VPATH name ${back_quote}(.*)'.*/){
	    $subtargetsnametoid_ref->{$1}=$subtargetsnametoid_ref->{$parent_target_name};
	}

	my @captures=();
	if(consume_and_capture("#\\s*(?:M|m)ake(?:\\[.*\\])?: Entering directory ${back_quote}(.*)'.*",\@captures)){
	    ($current_dir eq $captures[$#captures]) or die "Problem with current directory!";
	    if($debug){ print STDOUT "ENTERED ${current_dir} on line ${line_count}\n"; }
	}
	consume("\\s*(?:M|m)ake(?:\\[.*\\])?: ${back_quote}\Q${parent_target_name}\E' is up to date.*");
    }elsif(consume("\\s*Must remake target ${back_quote}\Q${parent_target_name}\E'.*")){
      body_exec($parent_target,$makefiles_ref,$current_dir,$subtargetsnametoid_ref,$parent_target_name) or die "Encountered following line during attempt to start execution of ${parent_target_name} on line ${line_count}: ${input}, stopped";
    }elsif(consume("\\s*Prerequisite ${back_quote}(.*)' of target ${back_quote}\Q${parent_target_name}\E' does not exist.*") or consume("\\s*Prerequisite ${back_quote}(.*)' is (newer)|(older) than target ${back_quote}\Q${parent_target_name}\E'.*") or consume("\\s*Target ${back_quote}\Q${parent_target_name}\E' is double-colon and has no prerequisites.*") or consume("\\s*Prerequisite ${back_quote}.*' is order-only for target ${back_quote}\Q${parent_target_name}\E'.*")){
      while(consume("\\s*Prerequisite ${back_quote}(.*)' of target ${back_quote}\Q${parent_target_name}\E' does not exist.*") or consume("\\s*Prerequisite ${back_quote}(.*)' is (newer)|(older) than target ${back_quote}\Q${parent_target_name}\E'.*") or consume("\\s*Target ${back_quote}\Q${parent_target_name}\E' is double-colon and has no prerequisites.*") or consume("\\s*Prerequisite ${back_quote}.*' is order-only for target ${back_quote}\Q${parent_target_name}\E'.*")){}

      if(consume("\\s*Must remake target ${back_quote}\Q${parent_target_name}\E'.*")){
	body_exec($parent_target,$makefiles_ref,$current_dir,$subtargetsnametoid_ref,$parent_target_name) or die "Encountered following line during attempt to start execution of ${parent_target_name} on line ${line_count}: ${input}, stopped";
      }elsif(consume("\\s*No need to remake target ${back_quote}\Q${parent_target_name}\E'.*")){
	  if($input =~ /.*using VPATH name ${back_quote}(.*)'.*/){
	      $subtargetsnametoid_ref->{$1}=$subtargetsnametoid_ref->{$parent_target_name};
	  }

	  my @captures=();
	  if(consume_and_capture("#\\s*(?:M|m)ake(?:\\[.*\\])?: Entering directory ${back_quote}(.*)'.*",\@captures)){
	      ($current_dir eq $captures[$#captures]) or die "Problem with current directory!";
	      if($debug){ print STDOUT "ENTERED ${current_dir} on line ${line_count}\n"; }
	  }
	  consume("\\s*(?:M|m)ake(?:\\[.*\\])?: ${back_quote}\Q${parent_target_name}\E' is up to date.*");
      }elsif(consume("\\s*No (commands|recipe) for ${back_quote}\Q${parent_target_name}\E' and no prerequisites actually changed.*")){
	      if(!consume("\\s*No need to remake target ${back_quote}\Q${parent_target_name}\E'.*")){ return 0; }
      }else{
	die "Encountered the following during decision-making on line ${line_count}: ${input}, stopped";
      }
    }else{
      die("Encountered following line during decision about execution on line ${line_count}: ${input}, stopped");
    }

    return 1;
}

sub body_exec {
    my ($parent_target,$makefiles_ref,$current_dir,$subtargetsnametoid_ref,$parent_target_name)=@_;
#    my $parent_target_name=$targets{$parent_target}->[$TARGETS_NAME];

    #my $gathered_output="";

    my @captures=();
    if(consume_and_capture("#\\s*(?:M|m)ake(?:\\[.*\\])?: Entering directory ${back_quote}(.*)'.*",\@captures)){
	my $this_dir=$captures[$#captures];
      ($current_dir eq $this_dir) or die "Problem with current directory: <${current_dir}> vs. <${this_dir}>!";
      if($debug){ print STDOUT "ENTERED ${current_dir} on line ${line_count}\n"; }
    }

    @captures=();
    my $stop=0;#prevent duplicate consuming

    if(consume("\\s*(?:M|m)ake(?:\\[.*\\])?: \\*\\*\\* No rule to make target ${back_quote}\Q${parent_target_name}\E'.*")){
      $error=-1;
      $targets{$subtargetsnametoid_ref->{$parent_target_name}}->[$TARGETS_ERROR]=$error;
      $stop=-1;
    }

    #possible that during execution of body multiple things have to be constructed in nested make-process + other output in between
    my $returned_from_recursive_make=0;
    #my $really_should_see_performance_measurement_of_recursive_make_now=0;
    until($stop or consume("\\s*Successfully remade target file ${back_quote}\Q${parent_target_name}\E'.*") or consume("\\s*Failed to remake target file ${back_quote}\Q${parent_target_name}\E'.*")){
      if(consume_banner()){
	start_new_make_process($parent_target);
	if($error){
	    $error=0;#restore until-loops + gather exact top-level error code
	}

	$returned_from_recursive_make=1;

	if($debugperf){
	  print STDERR ">>> RETURN1\n";
	}
	#$really_should_see_performance_measurement_of_recursive_make_now=0;
      }else{
	until(${error} or consume("\\s*Successfully remade target file ${back_quote}\Q${parent_target_name}\E'.*") or consume("\\s*Failed to remake target file ${back_quote}\Q${parent_target_name}\E'.*") or consume_banner()){
	  @captures=();

	    if(consume_and_capture("\\s*(?:M|m)ake(?:\\[.*\\])?: \\*\\*\\*\\s+\\[\Q${parent_target_name}\E\\]\\s*Error\\s*(\\d+).*",\@captures)){
		${error}=$captures[0];
		$targets{$subtargetsnametoid_ref->{$parent_target_name}}->[$TARGETS_ERROR]=$error;
		#timing information will probably be incorrect for recursive make, but there is functional error, so that one needs to be fixed first!
#	    }elsif(consume("^(?!\\+).*\Q${make_shell}\E ")){ #libtool often invoked with $SHELL by autotools, cf. glib-2.18.4 and friends, so ignore first time measurement following it (same for other commands using "$(SHELL) ...")
	    }elsif(consume("^\\s*\\+.*\Q${make_shell}\E ")){ #libtool often invoked with $SHELL by autotools, cf. glib-2.18.4 and friends, so ignore first time measurement following it (same for other commands using "$(SHELL) ...")
#	      if($returned_from_recursive_make){
#		$returned_from_recursive_make=0;
#
#		if($debugperf){
#		  print STDERR "<<< DISABLE RETURN 1\n";
#		}
#	      }
	      #$really_should_see_performance_measurement_of_recursive_make_now=0;
	      $explicit_shell_command_timer_running =()= $input =~ /\Q${make_shell}\E/g;#there could be more than one such timer in one line, so count exact number
#	      print STDERR "TIMER set to ${explicit_shell_command_timer_running}\n";
	      if($debug){
		print STDERR "===>timer running\n";
	      }
	    }elsif(consume_and_capture("^([0-9][\\.:0-9]+)user\\s+([0-9][\\.:0-9]+)system\\s+([0-9][\\.:0-9]+)elapsed",\@captures)){
	      #if we are not measuring time, we will never end up here, even if the consume-condition above was triggered (better than assuming that the SHELL variable contains "time")
	      if($debugperf){
		print STDERR "timing found for ${parent_target}\n";
	      }

	      if($explicit_shell_command_timer_running){
		$explicit_shell_command_timer_running--;
		if($debug){
		  print STDERR "+ timer stopped\n";
		}
	      }else{
		unless($returned_from_recursive_make){# and $really_should_see_performance_measurement_of_recursive_make_now){
		  #ignore timing of recursive make for time_without_recursive
		  #ERROR: what about for-loop recursive calls?
		  if($debugperf){
		    print STDERR "... even OWN\n";
		  }
		}else{
#		  if($returned_from_recursive_make){
		  if($debugperf){
		    print STDERR "<<< DISABLE RETURN 2\n";
		  }
		  
		  $returned_from_recursive_make=0;
		}
	      }

	      #$really_should_see_performance_measurement_of_recursive_make_now=0;
#	    }elsif(consume("\\s*# (?:M|m)ake(?:\\[.*\\])?: Leaving directory ${back_quote}(.*)'.*")){
#	      if($returned_from_recursive_make){
#		print STDERR "<<< LEAVING\n";
		#$really_should_see_performance_measurement_of_recursive_make_now=1;
#	      }
	    }elsif(consume_and_capture("^(\\+)+\\s+(.*)",\@captures)){
	      #implicit deps
	      if($debug){
		print STDOUT "${captures[1]}\n";
	      }
	      my $string=$captures[1];
	      $string =~ s/'/ /g;
	      $string =~ s/:/ /g;
	      $string =~ s/;/ /g;
#	      print STDOUT "${string}\n";

	      #extract macro constants
	      if(($string =~ m/gcc /) or ($string =~ m/g\+\+ /)){
		my $pid=$subtargetsnametoid_ref->{$parent_target_name};
		my %macros=();
		if(exists($targets{$pid}) and exists($targets{$pid}->[$TARGETS_MACROS])){
		  %macros = map { $_ => 1 } @{$targets{$pid}->[$TARGETS_MACROS]};
#		  my @tmp_ar=keys(%macros);
#		  print STDOUT "OLD macro: @{tmp_ar}\n";
		}

		while ($string =~ /-D((\S+)=?(\S+)?)\s+/g) {  # scalar context
		  $macros{$1}++;
		}
		my @tmp_ar=keys(%macros);
		$targets{$pid}->[$TARGETS_MACROS]=\@tmp_ar;		
#		print STDOUT "NEW macro: @{tmp_ar}\n";
	      }

	      my @string_comps=split(/ /,"${string}");
	      for my $str (@string_comps){
#		if(($str eq '.') or ($str eq '..')){
#		  ;
		if($str =~ /^\s*\.+\s*$/){
		  ;
		}elsif($str =~ /\-.*/){
#		  print STDOUT "THROWING away ${str}\n";
		  ;
		}elsif($str =~ /\*/){
#		  print STDOUT "THROWING away ${str} due to the star\n";
		  ;
		}elsif($str =~ /=/){
		    ;
		}elsif($str =~ /@/){
		    ;
		}elsif($str =~ /%/){
		    ;
		}elsif($str =~ /\(/){
		    ;
		}elsif($str =~ /\)/){
		    ;
		}elsif($str =~ /\|/){
		    ;
		}elsif(($str =~ /(\S+)\.(\S+)$/) and not $2 =~ /\// and not $str =~ /\\/ and not $2 =~ /^\d+\"?$/ and not $str =~ /\.\.\.+/){
		  $str =~ s/^\"//;#omit leading "
		  $str =~ s/\"$//;#omit trailing "
		  $str =~ s/^\`//;#omit leading `
		  $str =~ s/\`$//;#omit trailing `
		  $str =~ s/~\S+$//;#omit e.g. ...~ranlib
		  $str =~ s/^<//;#omit leading <
		  $str =~ s/>$//;#omit trailing >

		  if($str =~ /\$/ and not $str =~ /\.class$/){
		    next;#$-sign only makes sense in case of Java class?
		  }

		  my $full_target_name=resolve_target_name($str,$current_dir);#deal with duplicate targets
		  my $parent_target=$subtargetsnametoid_ref->{$parent_target_name};

		  if(exists($target_name_to_id{$full_target_name})){ 
		    my $new_id=$target_name_to_id{$full_target_name};

		    if($new_id eq $parent_target){
		      #omit looping implicit deps (target==implicit dep), as it's likely caused e.g. by "gcc file.c -o file.o" with "file.o" as target
		      if($debug){
			print STDOUT "IGNORING ${full_target_name} for ${new_id} and ${parent_target}!!!\n";
		      }
		    }elsif(not(existing_dependency($parent_target,$new_id))){
		      if($debug){
			print STDOUT "FOUND ${full_target_name}!!!\n";
		      }
		      register_target_and_edge($parent_target,$str,$current_dir,$subtargetsnametoid_ref,$makefiles_ref,0,1,0);
		      $implicit_dep_counter=$implicit_dep_counter+1;
		    }else{
		      if($debug){
			print STDOUT "IGNORING ${full_target_name} for ${new_id} and ${parent_target}...\n";
		      }
		    }
		  }else{ #it can't be the target or an explicit dependency, so we found an implicit one
		    if($debug){
		      print STDOUT "FOUND ${full_target_name}!!!\n";
		    }
		    register_target_and_edge($parent_target,$str,$current_dir,$subtargetsnametoid_ref,$makefiles_ref,0,1,0);
		    $implicit_dep_counter=$implicit_dep_counter+1;
		  }
		}
	      }
	    }else{
		consume(".*");
	    }
	  #$gathered_output .= $input;
	}
	
	if($error){
	    $stop=2;#error happened in this process
	}elsif(($input =~ /\s*Successfully remade target file ${back_quote}\Q${parent_target_name}\E'.*/) or ($input =~ /\s*Failed to remake target file ${back_quote}\Q${parent_target_name}\E'.*/)){
	  $stop=1;
	}else{ #banner
	  start_new_make_process($parent_target);
	  if($error){#error did NOT happen in this process
	      $error=0;#restore until-loops + gather exact top-level error code
	  }
	  $returned_from_recursive_make=1;

	  if($debugperf){
	    print STDERR ">>> RETURN2\n";
	  }
	}
      }
    }

    unless($error){
	@captures=();
	if(consume_and_capture("#\\s*(?:M|m)ake(?:\\[.*\\])?: Entering directory ${back_quote}(.*)'.*",\@captures)){
	    ($current_dir eq $captures[$#captures]) or die "Problem with current directory!";
	    if($debug){ print STDOUT "ENTERED ${current_dir} on line ${line_count}\n"; }
	    consume("\\s*(?:M|m)ake(?:\\[.*\\])?: Nothing to be done for ${back_quote}\Q${parent_target_name}\E'.*") or consume("\\s*(?:M|m)ake(?:\\[.*\\])?: ${back_quote}\Q${parent_target_name}\E' is up to date.*") or die("Expected a 'Nothing to be done for ${parent_target_name}' or '${parent_target_name} is up to date' on line ${line_count}, but found: ${input}\n");
	}
	
#wrong: no edge added!
#	while(consume("\\s*Pruning file ${back_quote}\Q${parent_target_name}\E'.*")){
	    #do nothing
#	}
    }

    if($error and ($input =~ /\s*Failed to remake target file ${back_quote}\Q${parent_target_name}\E'.*/) or consume("\\s*Failed to remake target file ${back_quote}\Q${parent_target_name}\E'.*")){
	$error=0;
    }

    return 1;
}

sub enter_database {
    my ($parent_target,$makefiles_ref,$subtargetsnametoid_ref,$current_dir)=@_;

    my %env_vars=();#name to value

    database_variables(\%env_vars) or die "Error during processing of variables section in makefile database on line ${line_count}.";
    if($eightyone or $eightytwo or $four){
	database_pattern_specific_variable_values() or die "Error during processing of pattern-specific variables section in makefile database on line ${line_count}.";
    }
    database_directories() or die "Error during processing of directories section in makefile database on line ${line_count}.";
    database_implicit_rules() or die "Error during processing of implicit rules section in makefile database on line ${line_count}.";
    if(not $eightyone and not $eightytwo and not $four){
	database_pattern_specific_variable_values() or die "Error during processing of pattern-specific variables section in makefile database on line ${line_count}.";
    }
    database_files($subtargetsnametoid_ref,$makefiles_ref,$current_dir,\%env_vars) or die "Error during processing of files section in makefile database on line ${line_count}.";
    database_vpath_search_paths() or die "Error during processing of vpath search paths section in makefile database on line ${line_count}.";
    if($eightyone or $eightytwo or $four){
	database_strcache() or die "Error no strcache comments found in makefile database on line ${line_count}.";
    }

    consume("\\s*# Finished Make data base on.*") or die "Make database ending expected on line ${line_count}, but found: ${input}, stopped";
    consume("\\s*# (?:M|m)ake(?:\\[.*\\])?: Leaving directory ${back_quote}(.*)'.*");# or die "Leaving directory expected on line ${line_count}, but found: ${input}, stopped";

    return 1;
}

sub database_variables {
  my ($env_vars_ref)=@_;

  if(!consume("\\s*# Variables.*")){ return 0; }

  my @captures=();

  until(consume("\\s*# variable set hash-table stats:.*")){
    ## automatic
    consume("#\\s+.*");
    #?F = $(notdir $?)
    if(consume_and_capture("(\\S+)\\s+:?=\\s+(.*)",\@captures)){
	$env_vars_ref->{$captures[0]}=$captures[1];
    }else{
      ($input =~ /\s*define.*/) or die "Expected define in variable section on line ${line_count}, but found: <${input}>.";

      until(consume("\\s*endef.*")){
	consume(".*");
      }
    }

    @captures=();
  }

  consume(".*");#skip extra line

  return 1;
}

sub database_directories {
  if(!consume("\\s*# Directories.*")){ return 0; }

  until(consume("\\s*# (.*) files, (.*) impossibilities in (.*) directories.*")){
    #skip for the moment
    consume(".*");
  }

  return 1;
}

sub database_implicit_rules{
  if(!consume("\\s*# Implicit Rules.*")){ return 0; }

  until(consume("\\s*# (.*) implicit rules, .* terminal.*") or consume("\\s*# No implicit rules\\..*")){
    #skip for the moment
    consume(".*");
  }

  return 1;
}

sub database_pattern_specific_variable_values{
  if(!consume("\\s*# Pattern-specific .ariable .alues.*")){ return 0; }

  until(consume("\\s*# (No|\\d+) pattern-specific variable values.*")){
    #skip for the moment
    consume(".*");
  }
  return 1;
}

sub database_strcache{
  if(!consume("\\s*# # of strings in strcache:.*") and !consume("\\s*# strcache buffers:\\s+\\d.*")){ return 0; }

  until(consume("\\s*# strcache free: total*") or consume("\\s*# strcache performance:\\s+lookups\\s+=.*")){
    #skip for the moment
    consume(".*");
  }

  if($eightytwo or $four){
    if (!consume("\\s*# strcache hash-table stats:") and !consume("\\s*# hash-table stats:")){ return 0;}
    if (!consume("\\s*# Load=.*")){ return 0;}
  }
  return 1;
}

sub database_files{
  my ($subtargetsnametoid_ref,$makefiles_ref,$current_dir,$env_vars_ref)=@_;

  if(!consume("\\s*# Files.*")){ return 0; }

  my $stop=0;
  until(consume("\\s*# files hash-table stats:.*") or (${stop}==2)){
    my @captures=();

    if(consume("#\\s+Not a target:.*")){
#      consume(".*");#skip the following 'name_target:'
    }elsif(consume_and_capture("^(\\S+)::.*",\@captures)){
      $stop=process_updated_target($captures[0],$subtargetsnametoid_ref,$makefiles_ref,$current_dir,$env_vars_ref);
    }elsif(consume_and_capture("^(\\S+):.*",\@captures)){
      $stop=process_updated_target($captures[0],$subtargetsnametoid_ref,$makefiles_ref,$current_dir,$env_vars_ref);
    }else{
      consume(".*");
    }
  }

  consume(".*");#skip extra line

  return 1;
}

sub process_updated_target {
      my ($target,$subtargetsnametoid_ref,$makefiles_ref,$current_dir,$env_vars_ref)=@_;

      my $phony=0;

      my @also_captures=();
      my $also_made_files_found=0;
      until(consume("#\\s+File has been updated.*") or consume("#\\s+File has not been updated.*")){
	  if(consume_and_capture("#\\s+Also makes:\\s+(.*)",\@also_captures)){
	      $also_made_files_found=1;
	  }elsif(consume("#\\s+Phony\\s+target.*")){
	      $phony=1;
	  }else{
	      consume(".*");
	  }
      }
      
      my %local_vars=();
      if($input =~ /#\s+File has been updated.*/){
	my @captures=();
	my $stop=0;
	until(${stop} or consume_and_capture("\\s*#\\s+(?:commands|recipe) to execute \\(from ${back_quote}(.*)', line (.*)\\).*",\@captures) or consume_and_capture("\\s*#\\s+(?:commands|recipe) to execute \\((.*)\\).*",\@captures) or consume("\\s*# files hash-table stats:.*")){
	    consume(".*");
	  
	    if($input =~ /#\s+Not a target:.*/){
#	    consume(".*");#skip the following 'name_target:'
		consume("^(\\S+):.*");
#	    $stop=1;
	      }elsif($input =~ /^#\s+(\S+)\s+:=\s+(.*)$/){
		$local_vars{$1}=$2;
	      }elsif($input =~ /^\s*# variable set hash-table stats:.*$/){
		consume("^\\s*#\\s+Load=\\d+.*");## Load=0/32=0%, Rehash=0, Collisions=0/96=0%
		consume("^(\\S+):.*");
	      }
	    
	    if($input =~ /^(\S+)::.*/){
		process_updated_target($1,$subtargetsnametoid_ref,$makefiles_ref,$current_dir,$env_vars_ref);
		$stop=1;
	    }elsif($input =~ /^(\S+):.*/){
		process_updated_target($1,$subtargetsnametoid_ref,$makefiles_ref,$current_dir,$env_vars_ref);
		$stop=1;
	    }
	    
	    @captures=();
	}
	
	if(($stop == 1)or(@captures == 0)){
	    push(@captures,"N/A","-1");#no makefile info or line number
	}elsif(@captures == 1){
	    push(@captures,"-1");#no line number otherwise
	}

	my @commands=();
	my @actual_commands=();
	if(($stop == 0) and (($input =~ /\s*#\s+(?:commands|recipe) to execute \(from ${back_quote}.*', line .*\).*/) or ($input =~ /\s*#\s+(?:commands|recipe) to execute \(.*\).*/))){
	    #gather commands
	    my @command=();
	    while(consume_and_capture("\t(.*)",\@command)){
		push(@commands,@command);
		my $actual_string=substitute($command[0],$env_vars_ref,\%local_vars);
#		print STDOUT "<${command[0]}> ===> <${actual_string}>\n";
		push(@actual_commands,$actual_string);
		@command=();
	    }
	}
	
	my $tmp=join(">, <",@captures);
	if($debug){ print STDOUT "FOUND <${target}> on line ${line_count}: <${tmp}>"; }
	
	my $id=$subtargetsnametoid_ref->{$target};
	
	if(defined($id)){
	    if($debug){ print STDOUT " ==> ID: ${id}\n"; }
	    $targets{$id}->[$TARGETS_MAKEFILE]=$captures[0];
	    $targets{$id}->[$TARGETS_LINE]=$captures[1];
	    #TODO: implicit deps
#	    add_implicit_deps($id,$current_dir,\@commands,$env_vars_ref);
	    $targets{$id}->[$TARGETS_COMMANDS]=\@commands;
	    $targets{$id}->[$TARGETS_ACTUAL_COMMANDS]=\@actual_commands;
	    $targets{$id}->[$TARGETS_PHONY]=$phony;

	    if($also_made_files_found){
	       # make edge from the also-made targets to the target under consideration to fix temporarily undefined messages
	       my @stringarray=split(/ /,$also_captures[0]);
	       for my $also_made_target (@stringarray){
		   if($debug){ print STDOUT " ===> DEFINING ${also_made_target} for ${target}!!!\n"; }
		   my $new_target=register_target($also_made_target,$subtargetsnametoid_ref,$makefiles_ref,$current_dir);
		   my $edge=register_edge($new_target,$id,0);
		   $edges{$edge}->[$EDGES_PRUNING]=0;
		   $edges{$edge}->[$EDGES_RECURSIVE]=0;
                   #impossible to use register_target_and_edge here, as new target should be parent!
#		   my $new_target=register_target_and_edge($parent_target,$captures[0],$current_dir,$subtargetsnametoid_ref,$makefiles_ref);

		   $targets{$new_target}->[$TARGETS_MAKEFILE]=$captures[0];
		   $targets{$new_target}->[$TARGETS_LINE]=$captures[1];
		   #TODO: implicit deps
#		   add_implicit_deps($new_target,$current_dir,\@commands,$env_vars_ref);
		   $targets{$new_target}->[$TARGETS_COMMANDS]=\@commands;
		   $targets{$new_target}->[$TARGETS_ACTUAL_COMMANDS]=\@actual_commands;
	       }
	   }
	}else{
	    #TODO: match .cpp.o, %.cpp, ... with keys of namestoid
	    #if($debug){ print STDOUT " <--> ${id} NOT DEFINED!!!\n"; }
	    if($debug){ print STDOUT " <--> ${target} NOT DEFINED on line ${line_count}!!!\n"; }
	}
	
	if($input =~ /\s*# files hash-table stats:.*/){
	    return 2;#stop
	}else{
	  return 1;
	}
      }elsif($input =~ /#\s+File has not been updated.*/ and exists($subtargetsnametoid_ref->{$target})){
	  my $id=$subtargetsnametoid_ref->{$target};

	  $targets{$id}->[$TARGETS_PHONY]=$phony;

	  if($targets{$id}->[$TARGETS_ERROR]){
	      my @captures=();

	      my $found_commands=0;

	      if(consume("\\s*# variable set hash-table stats:.*")){
		consume(".*");
		$found_commands=1;
	      }elsif($input =~ m/^\s*#\s+(?:commands|recipe) to execute/){ #firefox hack
		$found_commands=1;
	      }elsif(consume("\\s*# Not a target:.*")){
		#do nothing
	      }elsif($input =~ m/^(\S+)::?.*/){
		return 1;
	      }else{
		die "Expected data for erroneous target on line ${line_count}, but found: ${input}\n";
	      }

	      if($found_commands){
		consume_and_capture("\\s*#\\s+(?:commands|recipe) to execute \\(from ${back_quote}(.*)', line (.*)\\).*",\@captures) or consume_and_capture("\\s*#\\s+(?:commands|recipe) to execute \\((.*)\\).*",\@captures);
	      }

	      if(@captures == 1){
		  push(@captures,"-1");#no line number otherwise
	      }elsif(@captures == 0){
		  push(@captures,"N/A","-1");#no line number otherwise
	      }

	      my @commands=();
	      my @actual_commands=();

	      #gather commands
	      my @command=();
	      while(consume_and_capture("\t(.*)",\@command)){
		  push(@commands,@command);
		  my $actual_string=substitute($command[0],$env_vars_ref,\%local_vars);
#		  print STDOUT "<${command[0]}> ===> <${actual_string}>\n";
		  push(@actual_commands,$actual_string);
		  @command=();
	      }

	      my $tmp=join(">, <",@captures);
	      if($debug){ print STDOUT "FOUND erroneous <${target}> on line ${line_count}: <${tmp}>"; }
	      if($debug){ print STDOUT " ==> ID: ${id}\n"; }
	      $targets{$id}->[$TARGETS_MAKEFILE]=$captures[0];
	      $targets{$id}->[$TARGETS_LINE]=$captures[1];
	      #TODO: implicit deps
#	      add_implicit_deps($id,$current_dir,\@commands,$env_vars_ref);
	      $targets{$id}->[$TARGETS_COMMANDS]=\@commands;
	      $targets{$id}->[$TARGETS_ACTUAL_COMMANDS]=\@actual_commands;
	  }

	  return 1;
      }elsif($unused and $input =~ /#\s+File has not been updated.*/){
	  if(not($target =~ /^\./)){
	      my $full_target_name=resolve_target_name($target,$current_dir);
	      if(register_unused_target($target,$current_dir,$full_target_name)){
		  $unused_target_counter=$unused_target_counter+1;

		  my $id=$full_target_name;
		  my @captures=();

#		  if(consume("\\s*# variable set hash-table stats:.*")){
#		      consume(".*");
		  consume_and_capture("\\s*#\\s+(?:commands|recipe) to execute \\(from ${back_quote}(.*)', line (.*)\\).*",\@captures) or consume_and_capture("\\s*#\\s+(?:commands|recipe) to execute \\((.*)\\).*",\@captures);
#		  }elsif(consume("\\s*# Not a target:.*")){
		      #do nothing
#		  }else{
#		      die "Expected data for erroneous target on line ${line_count}, but found: ${input}\n";
#		  }
		  
		  if(@captures == 1){
		      push(@captures,"-1");#no line number otherwise
		  }elsif(@captures == 0){
		      push(@captures,"N/A","-1");#no line number otherwise
		  }
		  
		  my @commands=();
		  my @actual_commands=();
		  
		  #gather commands
		  my @command=();
		  while(consume_and_capture("\t(.*)",\@command)){
		      push(@commands,@command);
		      my $actual_string=substitute($command[0],$env_vars_ref,\%local_vars);
#		      print STDOUT "<${command[0]}> ===> <${actual_string}>\n";
		      push(@actual_commands,$actual_string);
		      @command=();
		  }
		  
		  my $tmp=join(">, <",@captures);
		  if($debug){ print STDOUT "FOUND erroneous unused <${target}> on line ${line_count}: <${tmp}>"; }
		  if($debug){ print STDOUT " ==> ID: ${id}\n"; }
		  $unused_targets{$id}->[$TARGETS_MAKEFILE]=$captures[0];
		  $unused_targets{$id}->[$TARGETS_LINE]=$captures[1];
		  #TODO: implicit deps
#	      add_implicit_deps($id,$current_dir,\@commands,$env_vars_ref);
		  $unused_targets{$id}->[$TARGETS_COMMANDS]=\@commands;
		  $unused_targets{$id}->[$TARGETS_ACTUAL_COMMANDS]=\@actual_commands;

		  if($debug){
		      print STDOUT "FOUND unused target: ${target} -> ${full_target_name}\n";
		  }
	      }
	  }
	  
	  return 1;
      }
}

sub database_vpath_search_paths{
  if(!consume("\\s*# VPATH Search Paths.*")){ return 0; }

  until(consume("\\s*# ((No g)|(G))eneral \\(${back_quote}VPATH' variable\\) search path.*")){
    #skip for the moment
    consume(".*");
  }

  if($input =~ /\s*# General \(${back_quote}VPATH' variable\) search path.*/){
    consume(".*");#skip extra line
  }

  return 1;
}

# ===================================================================
# detect implicit deps                                              =
# ===================================================================

#sub dumpnode {
#    my $self = shift;
#    my %args = @_;
#    print "$args{type}: <$args{token}>\n"
#}
#
#{
#  my $structure_counter=0;#({}) does NOT work!
#  my $string_counter=0;#"'`
#
#  sub filter_metachar {
#    my $self=shift;
#    my %args = @_;
#    
#    my $text=$args{token};
#    print STDOUT "TEXT: <${text}>\n";
#    
#    if(($text eq "\"") or ($text eq "\'") or ($text eq "`")){
#      if($string_counter){
#	$string_counter=0;
#      }else{
#	$string_counter=1;
#      }
#    }elsif(($text eq "(") or ($text eq "{")){
#      $structure_counter=$structure_counter+1;
#    }elsif(($text eq ")") or ($text eq "}")){
#      $structure_counter=$structure_counter-1;
#    }else{
#      print "$args{type}: <${text}>\n"
#    }
#
##    print STDOUT "<${string_counter}>-<${structure_counter}>\n";
#  }
#  
#  sub filter_text {
#    my $self=shift;
#    my %args = @_;
#    
#    my $text=$args{token};
#    
#    if(($text =~ /^\".*\"$/) or ($text =~ /^\'.*\'$/)){
#      #ignore
#      #print STDOUT "IGNORING: <$text>\n";
#    }elsif($text =~ /^-/){
#      #ignore
#    }else{
#      print "$args{type}: <$args{token}>\n"
#    }
#  }
#}
#
#sub filter_variable {
#  my $self=shift;
#  my %args = @_;
#
#  my $text=$args{token};
#
##  if(($text =~ /^\".*\"$/) or ($text =~ /^\'.*\'$/)){
#    #ignore
#    #print STDOUT "IGNORING: <$text>\n";
##  }
#}
#
#sub filter_builtin {
#  my $self=shift;
#  my %args = @_;
#
#  my $text=$args{token};
#
##  if(($text =~ /^\".*\"$/) or ($text =~ /^\'.*\'$/)){
#    #ignore
#    #print STDOUT "IGNORING: <$text>\n";
##  }
#}
#
#sub filter_keyword {
#  my $self=shift;
#  my %args = @_;
#
#  my $text=$args{token};
#
##  if(($text =~ /^\".*\"$/) or ($text =~ /^\'.*\'$/)){
#    #ignore
#    #print STDOUT "IGNORING: <$text>\n";
##  }
#}

#sub substitute_vars{
#  my ($var_name,$full_expr,$env_vars_ref,$did_i_substitute_something_ref)=@_;

##  my @keys=keys(%{$env_vars_ref});
##  my $str=join("\n",@keys);
##  my $str=@keys;
##  print STDOUT "use: $str\n";
##  print STDOUT "TEST: <${var_name}> -> <$full_expr>\n";

#  if(exists($env_vars_ref->{$var_name})){
#    ${$did_i_substitute_something_ref}=1;
##    my $tmp=$env_vars_ref->{$var_name};
##    print STDOUT "VALUE: ${tmp}\n";
#    return $env_vars_ref->{$var_name};
#  }else{
#    ${$did_i_substitute_something_ref}=0;
#    return $full_expr;
#  }
#}

# sub add_implicit_deps {
#   my ($id,$current_dir,$commands_ref,$env_vars_ref)=@_;

#   my @possible_deps=();
#   my @new_commands=();
# }

# sub add_implicit_deps_old {
#   my ($id,$current_dir,$commands_ref,$env_vars_ref)=@_;

#   my @possible_deps=();
#   my @new_commands=();

#   for my $comm(@{$commands_ref}){
#     my $command=$comm;#do not modify original command, because weaving could be much harder (no variables anymore)!
#     my $did_i_substitute_something=($command =~ /\$[\{\(](\w+)[\}\)]/);#if no match, loop body will not execute

#     if($debug){
#       print STDOUT "ORIG: ${command}\n";
#     }

#     while($did_i_substitute_something and $command =~ s/\$[\{\(](\w+)[\}\)]/substitute_vars($1,$&,$env_vars_ref,\$did_i_substitute_something)/ge){#/
# #	 print STDOUT "SUBS: ${command}\n";
#     }
    
#     if($debug){
#       print STDOUT "FINAL: ${command}\n";
#     }
#     push(@new_commands,$command);
#   }

#   my $parser = new Shell::Parser(syntax => 'make',handlers => { default => \&dumpnode,text => \&filter_text,variable => \&filter_variable,builtin => \&filter_builtin,keyword => \&filter_keyword,metachar => \&filter_metachar });
#   $parser->parse($debug,join("\n",@new_commands));

# #  for my $command (@{$commands_ref}){
# #    my @parts=split(/\s+/,$command);
# #
# #    my $index=0;
# #    for my $part (@parts){		    
# #	if($part =~ /^#/){
# #	    last;#comment, so skip rest of line
# #	}elsif($part =~ /^[\"\\\*`\-\{\'|&]/){
# #	    #ignore
# #	}elsif($part =~ /^\.+$/){
# #	    #ignore
# #	}elsif(($index == 0) and (($part =~ /[mM][aA][kK][eE]/))){
# #	    last;
# #	}elsif($index == 0){
# #	    #ignore
# #	}elsif($part =~ /\*$/){
# #	    #ignore
# #	}elsif(($part =~ /[cC][hH][mM][oO][dD]/) or ($part =~ /[mM][kK][dD][iI][rR]/) or ($part =~ /[fF][iI][nN][dD]/) or ($part =~ /[eE][cC][hH][oO]/) or ($part =~ /[mM][vV]/) or ($part =~ /[eE][xX][iI][tT]/) or ($part =~ /[rR][mM]/)){
# #	}elsif($part =~ /^\d+/){
# #	    #ignore
# #	}elsif(($part =~ /^\$</) or ($part =~ /^\$@/) or ($part =~ /^\$\?/)){
# #	    #ignore
# #	}elsif($part =~ /:/){
# #	    #ignore
# #	}elsif($part =~ /^\$/){
# #	    my $tmp=substitute($part,$env_vars_ref);
# #	    unless($tmp eq $part){
# #		push(@possible_deps,$tmp);
# #		print STDOUT "${command}: ${tmp}\n";
# #	    }
# #	}else{
# #	    push(@possible_deps,$part);
# #	    print STDOUT "${command}: ${part}\n";
# #	}
# #	$index++;
# #    }
# #  }

#   for my $possible_dep (@possible_deps){
#       #register_target + makefile 
# #      print STDOUT "${possible_dep}\n";
#   }
# }

sub substitute{
    my ($string,$env_vars_ref,$local_vars_ref)=@_;

    my @parts=split(/\s+/,$string);
    my @res=();

    for my $part (@parts){
#print STDOUT "START <${part}>\n";
      my @subparts=split(/\$/,$part);
      my @subres=();

      my $index=0;
      for my $subpart (@subparts){
#print STDOUT "START2 <${subpart}>\n";
	if($index>0){
	  $subpart = "\$${subpart}";
	}

	$index++;

	if(($subpart =~ /(\$\{(\S+)\})/) or ($subpart =~ /(\$\((\S+)\*?\))/) or ($subpart =~ /(\$(\S+))\*?;?/)){
	  my $whole=$1;
	  my $var=$2;
	  $var =~ s/'//g;
	  $var =~ s/;//g;
	  $var =~ s/\*\)//g;
	  $var =~ s/"//g;
	  $var =~ s/\)$//g;
#	  print STDOUT "CHECKING ${whole}, in particular ${var}\n";
	  
	  
	  if(exists($env_vars_ref->{$var})){
	    my $subst=substitute("$env_vars_ref->{$var}",$env_vars_ref,$local_vars_ref);
#print STDOUT "LOC: ${subpart} => ${subst}\n";
	    #$subpart =~ s/$whole/${subst}/g;
	    if($subpart =~ /\$\{\Q${var}\E\}/){
	      $subpart =~ s/\$\{\Q${var}\E\}/${subst}/;
	    }elsif($subpart =~ /\$\(\Q${var}\E\)/){
	      $subpart =~ s/\$\(\Q${var}\E\)/${subst}/;
	    }else{
	      $subpart =~ s/\$\Q${var}\E/${subst}/;
	    }
#print STDOUT "AFTER: ${subpart}\n";
	  }elsif(exists($local_vars_ref->{$var})){
	    my $subst=substitute("$local_vars_ref->{$var}",$env_vars_ref,$local_vars_ref);
#print STDOUT "ENV: ${subpart} => ${subst}\n";
	    #$subpart =~ s/$whole/${subst}/g;
	    if($subpart =~ /\$\{\Q${var}\E\}/){
	      $subpart =~ s/\$\{\Q${var}\E\}/${subst}/;
	    }elsif($subpart =~ /\$\(\Q${var}\E\)/){
	      $subpart =~ s/\$\(\Q${var}\E\)/${subst}/;
	    }else{
	      $subpart =~ s/\$\Q${var}\E/${subst}/;
	    }
#print STDOUT "AFTER: ${subpart}\n";
	  }
	}

	push(@subres,$subpart);
      }


      push(@res,join('',@subres));
	
    }

    return join(' ',@res);
}

# ===================================================================
# .gdf generator methods...                                         =
# ===================================================================

sub write_gdf_targets {
  my ($main_target,$unused_name_to_id_ref)=@_;
  #  print $HANDLE_OUT "nodedef> name,localname VARCHAR(255),makefile VARCHAR(255),line INT,style,concern VARCHAR(50),ismeta INT,error INT,tstamp INT\n";
  print $HANDLE_OUT "nodedef> name,localname VARCHAR(255),makefile VARCHAR(255),line INT,style,concern VARCHAR(50),error INT,tstamp INT,phony INT,dir VARCHAR(255),base VARCHAR(255),inuse INT\n";

  for my $key (keys(%targets)){
    my @data=@{$targets{$key}};

    my $concern=$key;
    if ($concern =~ /^.*_(\S*)$/){#use extension as indicator for concern
      $concern=$+;
    }
    $concern =~ s/ /___/g;

    my $style=2;
    if($key eq $main_target){
      $style=8;
    }

#    print $HANDLE_OUT "${key},${data[${TARGETS_NAME}]},${data[${TARGETS_MAKEFILE}]},${data[${TARGETS_LINE}]},${style},${concern},${data[${TARGETS_META}]},${data[${TARGETS_ERROR}]},${data[${TARGETS_TIME}]}\n";
    #See drivers/scsi/53c7,8xx.c
    my $commaless_name=${data[${TARGETS_NAME}]};
    $commaless_name =~ s/,/_/g;

    my $commaless_base_name=${data[${TARGETS_BASENAME}]};
    $commaless_base_name =~ s/,/_/g;

    #eliminate whitespace in name, localname, makefile and dir
    $key =~ s/ /___/g;
    $commaless_name =~ s/ /___/g;
    $commaless_base_name =~ s/ /___/g;
    my $targets_makefile=${data[${TARGETS_MAKEFILE}]};
    $targets_makefile =~ s/ /___/g;
    my $targets_dirname=${data[${TARGETS_DIRNAME}]};
    $targets_dirname =~ s/ /___/g;

    print $HANDLE_OUT "${key},${commaless_name},${targets_makefile},${data[${TARGETS_LINE}]},${style},${concern},${data[${TARGETS_ERROR}]},${data[${TARGETS_TIME}]},${data[${TARGETS_PHONY}]},${targets_dirname},${commaless_base_name},${data[${TARGETS_INUSE}]}\n";
  }

  for my $key (keys(%unused_targets)){
    my @data=@{$unused_targets{$key}};

    if(exists($target_name_to_id{$key})){
	$unused_target_counter=$unused_target_counter-1;
#	$target_count=$target_count-1;
    }else{

	my $new_key=create_target_id(${data[${TARGETS_NAME}]});
	$unused_name_to_id_ref->{$key}=$new_key;

	my $concern=$new_key;
	if ($concern =~ /^.*_(\S*)$/){#use extension as indicator for concern
	    $concern=$+;
	}
	$concern =~ s/ /___/g;

	my $style=2;

#    print $HANDLE_OUT "${key},${data[${TARGETS_NAME}]},${data[${TARGETS_MAKEFILE}]},${data[${TARGETS_LINE}]},${style},${concern},${data[${TARGETS_META}]},${data[${TARGETS_ERROR}]},${data[${TARGETS_TIME}]}\n";

	#eliminate whitespace in name, localname, makefile and dir
	$new_key =~ s/ /___/g;
	my $targets_name=${data[${TARGETS_NAME}]};
	$targets_name =~ s/ /___/g;
	my $targets_makefile=${data[${TARGETS_MAKEFILE}]};
	$targets_makefile =~ s/ /___/g;
	my $targets_dirname=${data[${TARGETS_DIRNAME}]};
	$targets_dirname =~ s/ /___/g;
	my $targets_basename=${data[${TARGETS_BASENAME}]};
	$targets_basename =~ s/ /___/g;

	print $HANDLE_OUT "${new_key},${targets_name},${targets_makefile},${data[${TARGETS_LINE}]},${style},${concern},${data[${TARGETS_ERROR}]},${data[${TARGETS_TIME}]},${data[${TARGETS_PHONY}]},${targets_dirname},${targets_basename},${data[${TARGETS_INUSE}]}\n";
    }
  }

  $target_count=$target_count-$unused_target_counter;#correct: create_target_id increments counter!

}

sub write_gdf_edges {
#  my %detect_duplicates=();#unneeded, as GUESS can handle it
  print $HANDLE_OUT "edgedef> node1,node2,directed,ismeta INT,tstamp INT,pruning INT,implicit INT,recursive INT\n";

  my $total_count=0;

  for my $node (keys(%edges_src_to_dst)){
    my $count=@{$edges_src_to_dst{$node}};
    $total_count=$total_count+$count;
  }

  ($total_count == $edge_count) or die "Found ${total_count} edges instead of ${edge_count}!";

  for my $edge (keys(%edges)) {
    my $src=$edges{$edge}->[$EDGES_SRC];
    my $dst=$edges{$edge}->[$EDGES_DST];
    my $type=$edges{$edge}->[$EDGES_TYPE];
    my $edge_time=$edges{$edge}->[$EDGES_TIME];
    my $pruning=$edges{$edge}->[$EDGES_PRUNING];
    my $implicit=$edges{$edge}->[$EDGES_IMPLICIT];
    my $recursive=$edges{$edge}->[$EDGES_RECURSIVE];

 #   if(exists($detect_duplicates{$src})&&($detect_duplicates{$src} eq $dst)){
      #do nothing
#    }els
    if ($src ne $dummy_target){
      # detect duplicates of both $src and $dst and replace them by merged targets
#      while(exists($duplicate_to_merged_targets{$src})){
#	$src=$duplicate_to_merged_targets{$src};
#      }
#      while(exists($duplicate_to_merged_targets{$dst})){
#	$dst=$duplicate_to_merged_targets{$dst};
#      }

      #eliminate whitespace in node1 and node2
      $src =~ s/ /___/g;
      $dst =~ s/ /___/g;
      print $HANDLE_OUT "$src,$dst,true,$type,$edge_time,$pruning,$implicit,$recursive\n";
    }else{
      if ($debug){
	print STDERR "!!! Removing virtual edge ($src,$dst)...\n";
      }
      delete($edges{$edge});
      $edge_count--;#no real edge
    }
  }
}

sub init_xml_file {
  my $writer=new XML::Writer( OUTPUT => $HANDLE_XML, DATA_MODE => "true", DATA_INDENT => 2 );

  $writer->xmlDecl("UTF-8");
  $writer->startTag("build");

  return $writer;
}

sub write_xml_data {
    my ($main_target,$unused_name_to_id_ref,$writer)=@_;

#    use XML::Writer;
#    my $writer = new XML::Writer( OUTPUT => $HANDLE_XML, DATA_MODE => "true", DATA_INDENT => 2 );

#    $writer->xmlDecl("UTF-8");
#    $writer->startTag("build", "name" => "${main_target}");

    for my $key (keys(%targets)){
	my @commands=@{$targets{$key}->[$TARGETS_COMMANDS]};
	my @actual_commands=@{$targets{$key}->[$TARGETS_ACTUAL_COMMANDS]};
	my @macros=@{$targets{$key}->[$TARGETS_MACROS]};

	#eliminate spaces in key to be in sync with gdf file
	$key =~ s/ /___/g;
	$writer->startTag("target", "name" => "${key}");
	for my $command (@commands){
	    $writer->dataElement("command","$command");
	}
	for my $actual_command (@actual_commands){
	    $writer->dataElement("actual_command","$actual_command");
	}
	for my $macro (@macros){
	    $writer->dataElement("macro","$macro");
	}
	$writer->endTag();#target
    }

    for my $key (keys(%unused_targets)){
	unless(exists($target_name_to_id{$key})){
	    my @commands=@{$unused_targets{$key}->[$TARGETS_COMMANDS]};
	    my @actual_commands=@{$unused_targets{$key}->[$TARGETS_ACTUAL_COMMANDS]};
	    my @macros=@{$unused_targets{$key}->[$TARGETS_MACROS]};

	    my $new_key=$unused_name_to_id_ref->{$key};
	    #eliminate spaces in key to be in sync with gdf file
	    $new_key =~ s/ /___/g;

	    $writer->startTag("target", "name" => "${new_key}");
	    for my $command (@commands){
		$writer->dataElement("command","$command");
	    }
	    for my $actual_command (@actual_commands){
		$writer->dataElement("actual_command","$actual_command");
	    }
	    for my $macro (@macros){
	      $writer->dataElement("macro","$macro");
	    }
	    $writer->endTag();#target
	}
    }

    $writer->endTag();#build
    $writer->end();
}

sub write_xml_data_for_prolog {
    my ($main_target,$unused_name_to_id_ref,$writer)=@_;

#    use XML::Writer;
#    my $writer = new XML::Writer( OUTPUT => $HANDLE_XML, DATA_MODE => "true", DATA_INDENT => 2 );

#    $writer->xmlDecl("UTF-8");
#    $writer->startTag("build", "name" => "${main_target}");

    for my $key (keys(%targets)){
	my @commands=@{$targets{$key}->[$TARGETS_COMMANDS]};
	my @actual_commands=@{$targets{$key}->[$TARGETS_ACTUAL_COMMANDS]};
	my @macros=@{$targets{$key}->[$TARGETS_MACROS]};

	#eliminate spaces in key to be in sync with gdf file
	$key =~ s/ /___/g;
	if ($key =~ /^(t[0-9]+)_.*$/){
	  $writer->startTag("target", "name" => "${1}");
	}else {
	  #start node name
#	  print STDOUT ("Weird key: $key\n");
	  $writer->startTag("target", "name" => "${key}");
	}
	
	for my $command (@commands){
	    $writer->dataElement("command","$command");
	}
	for my $actual_command (@actual_commands){
	    $writer->dataElement("actual_command","$actual_command");
	}
	for my $macro (@macros){
	    $writer->dataElement("macro","$macro");
	}
	$writer->endTag();#target
    }

    for my $key (keys(%unused_targets)){
	unless(exists($target_name_to_id{$key})){
	    my @commands=@{$unused_targets{$key}->[$TARGETS_COMMANDS]};
	    my @actual_commands=@{$unused_targets{$key}->[$TARGETS_ACTUAL_COMMANDS]};
	    my @macros=@{$unused_targets{$key}->[$TARGETS_MACROS]};

	    my $new_key=$unused_name_to_id_ref->{$key};
	    #eliminate spaces in key to be in sync with gdf file
	    $new_key =~ s/ /___/g;
	    if ($new_key =~ /^(t[0-9]+)_.*$/){
	      $writer->startTag("target", "name" => "${1}");
	    }else {
	      print STDOUT ("Weird key: $new_key\n");
	      $writer->startTag("target", "name" => "${new_key}");
	    }

	    for my $command (@commands){
		$writer->dataElement("command","$command");
	    }
	    for my $actual_command (@actual_commands){
		$writer->dataElement("actual_command","$actual_command");
	    }
	    for my $macro (@macros){
	      $writer->dataElement("macro","$macro");
	    }
	    $writer->endTag();#target
	}
    }

    $writer->endTag();#build
    $writer->end();
}

# =====================================================================
# .vrmlgraph generator methods (http://vrmlgraph.i-scream.org.uk/)... =
# =====================================================================

sub write_vrmlgraph_edges {
#  my %detect_duplicates=();#unneeded, as vrmlgraph can handle it
  print $HANDLE_OUT "# Generated using MAKAO Explorer ${current_version}\n";

  for my $edge (keys(%edges)) {
    my $src=$edges{$edge}->[$EDGES_SRC];
    my $dst=$edges{$edge}->[$EDGES_DST];

 #   if(exists($detect_duplicates{$src})&&($detect_duplicates{$src} eq $dst)){
      #do nothing
#    }els
    if ($src ne $dummy_target){
#      $detect_duplicates{$src}=$dst;
      #eliminate spaces in src and dst to be in sync with gdf file
      $src =~ s/ /___/g;
      $dst =~ s/ /___/g;
      print $HANDLE_OUT "$src $dst\n";
    }else{
      if ($debug){
	print STDERR "!!! Removing virtual edge ($src,$dst)...\n";
      }
      delete($edges{$edge});
      $edge_count--;#no real edge
    }
  }
}

# =====================================================================
# .ncol generator methods (http://apropos.icmb.utexas.edu/lgl/)...    =
# =====================================================================

sub write_ncol_edges {
  my %detect_duplicates=();#src to list of dst's
#  print $HANDLE_OUT "# Generated using MAKAO Explorer ${current_version}\n";

  for my $edge (keys(%edges)) {
    my $src=$edges{$edge}->[$EDGES_SRC];
    my $dst=$edges{$edge}->[$EDGES_DST];

   if(exists($detect_duplicates{$src})&&(contains_text($dst,$detect_duplicates{$src}))){
      #do nothing
    }elsif ($src ne $dummy_target){

      if(!exists($detect_duplicates{$src})){
	$detect_duplicates{$src}=();
      }

      
      push(@{$detect_duplicates{$src}},$dst);

      #eliminate spaces in key to be in sync with gdf file
      $src =~ s/ /___/g;
      $dst =~ s/ /___/g;
      print $HANDLE_OUT "$src $dst\n";
    }else{
      if ($debug){
	print STDERR "!!! Removing virtual edge ($src,$dst)...\n";
      }
      delete($edges{$edge});
      $edge_count--;#no real edge
    }
  }
}

# ===================================================================
# Prolog generator methods...                                       =
# ===================================================================

sub write_prolog {
  my ($main_target)=@_;
  #print $HANDLE_OUT ("main_target($main_target).\n");

  my $targets = "";
  my $target_concerns = "";
  my $phonies = "";
  my $build_times = "";
  my $makefiles = "";
  my $in_makefile = "";
  my $build_errors = "";
  my $paths_to_targets = "";

  my %makefiles;

  for my $key (keys(%targets)){
    my @data=@{$targets{$key}};

    if ($key =~ /^(t[0-9]+)_.*$/){
      $key=$1;
    } elsif ($key eq $main_target) {
      $key =~ s/ /___/g;
      print $HANDLE_OUT ("main_target($key).\n");
    } else {
      print STDOUT ("Weird key: $key\n");
    }

    my $full_path=$data[$TARGETS_DIRNAME]."/".$data[$TARGETS_BASENAME];
    $full_path =~ s/ /___/g;
    my @path = split('/', $full_path);
    my $path_as_list = "[";
    my $index = 0;
    foreach my $part (@path) {
	    last if ($index == (@path - 1));
	    $path_as_list .= ", " unless ($index == 0);
	    $path_as_list .= "'" . $part . "'";
	    $index++;
    }
    $path_as_list .= "]";

    my $target_name = $path[@path - 1];
    my $makefile_key = $makefiles{$data[$TARGETS_MAKEFILE]};

    if (not exists $makefiles{$data[$TARGETS_MAKEFILE]}) {
      $makefile_key = "m" . keys( %makefiles );
      $makefiles{$data[$TARGETS_MAKEFILE]} = $makefile_key;

      my @makefile = split('/', $data[$TARGETS_MAKEFILE]);
      my $makefile_path_as_list = "[";
      $index = 0;
      foreach my $part (@makefile) {
	last if ($index == (@path - 1));
	$makefile_path_as_list .= ", " unless ($index == 0);
	$part =~ s/ /___/g;
	$makefile_path_as_list .= "'" . $part . "'";
	$index++;
      }
      $makefile_path_as_list .= "]";
      my $makefile_name = $makefile[@makefile - 1];
      $makefile_name =~ s/ /___/g;
      $makefile_key =~ s/ /___/g;

      $makefiles .= "makefile($makefile_key, $makefile_path_as_list, '$makefile_name', ${data[${TARGETS_LINE}]}).\n";
    }

    my $extension = "";
    if ($target_name =~ /^(.*)\.([^\.]+)$/) {
      $extension = $2 unless ($1 eq "");
    }
    $extension =~ s/ /___/g;

    $targets .= "target($key, '$target_name').\n";
    $in_makefile .= "in_makefile($key, $makefile_key).\n";
    $target_concerns .= "target_concern($key, '$extension').\n" unless ($extension eq "");
    $phonies .= "phony_target($key).\n" if ($data[$TARGETS_PHONY]);
    $build_times .= "build_time($key, ${data[${TARGETS_TIME}]}).\n";
    $build_errors .= "build_error($key).\n" if ($data[$TARGETS_ERROR]);
    $paths_to_targets .= "path_to_target($key, $path_as_list).\n";

    # ${key},${data[${TARGETS_NAME}]},${data[${TARGETS_MAKEFILE}]},
    # ${data[${TARGETS_LINE}]},${style},${concern},
    # ${data[${TARGETS_ERROR}]},${data[${TARGETS_TIME}]},
    # ${data[${TARGETS_PHONY}]},${data[${TARGETS_PATH}]}\n";
  }

  print $HANDLE_OUT ($targets);
  print $HANDLE_OUT ($in_makefile);
  print $HANDLE_OUT ($target_concerns);
  print $HANDLE_OUT ($phonies);
  print $HANDLE_OUT ($build_times);
  print $HANDLE_OUT ($build_errors);
  print $HANDLE_OUT ($paths_to_targets);
  print $HANDLE_OUT ($makefiles);

  my $dependencies = "";
  my $dependency_types = "";
  my $dependency_times = "";
  my $dependencies_pruned = "";
  my $dependencies_implicit = "";
  my $dependencies_recursive = "";

  for my $edge (keys(%edges)) {
    my $src=$edges{$edge}->[$EDGES_SRC];
    my $dst=$edges{$edge}->[$EDGES_DST];
    my $type=$edges{$edge}->[$EDGES_TYPE];
    my $edge_time=$edges{$edge}->[$EDGES_TIME];
    my $pruning=$edges{$edge}->[$EDGES_PRUNING];
    my $implicit=$edges{$edge}->[$EDGES_IMPLICIT];
    my $recursive=$edges{$edge}->[$EDGES_RECURSIVE];

    my $src_key = $src;
    if ($src =~ /^(t[0-9]+)_.*$/){
      $src_key=$1;
    } elsif ($src eq $main_target) {
	  # main target
    } else {
	  print STDOUT ("Weird key: $src\n");
    }

    my $dst_key = $dst;
    if ($dst =~ /^(t[0-9]+)_.*$/){
      $dst_key=$1;
    } elsif ($dst eq $main_target) {
	  # main target
    } else {
	  print STDOUT ("Weird key: $dst\n");
    }

    my $dep_key = $src_key . ":" . $dst_key;

    if ($src ne $dummy_target){
      # detect duplicates of both $src and $dst and replace them by merged targets
#      while(exists($duplicate_to_merged_targets{$src})){
#		$src=$duplicate_to_merged_targets{$src};
#      }
#      while(exists($duplicate_to_merged_targets{$dst})){
#		$dst=$duplicate_to_merged_targets{$dst};
#      }

      $src_key =~ s/ /___/g;
      $dst_key =~ s/ /___/g;
      $dependencies .= "dependency($src_key, $dst_key, $dep_key).\n";
      $dependency_types .= "dependency_ismeta($dep_key).\n" if($type);
      $dependency_times .= "dependency_time($dep_key, $edge_time).\n";
      $dependencies_pruned .= "dependency_pruned($dep_key).\n" if($pruning);
      $dependencies_implicit .= "dependency_implicit($dep_key).\n" if($implicit);
      $dependencies_recursive .= "dependency_recursive($dep_key).\n" if($recursive);
    }else{
      if ($debug){
		print STDERR "!!! Removing virtual edge ($src,$dst)...\n";
      }
      delete($edges{$edge});
      $edge_count--;#no real edge
    }
  }

  print $HANDLE_OUT ($dependencies);
  print $HANDLE_OUT ($dependency_types);
  print $HANDLE_OUT ($dependency_times);
  print $HANDLE_OUT ($dependencies_pruned);
  print $HANDLE_OUT ($dependencies_implicit);
  print $HANDLE_OUT ($dependencies_recursive);

}


# ===================================================================
# Utility methods...                                                =
# ===================================================================

#returns $dummy_target if $new_target does not exist yet
sub existing_target {
  my ($new_target,$subtargetsnametoid_ref,$makefiles_ref,$current_dir_name,$full_target_name)=@_;

  my $id="";

    if(exists($subtargetsnametoid_ref->{$new_target})){
      $id=$subtargetsnametoid_ref->{$new_target};

      #possibly update meta status
      my $ismeta=0;
      if(contains_text($new_target,$makefiles_ref)){#do NOT look at $busy_on_meta_level, as root target would otherwise be falsely recognised as meta
	$ismeta=1;
      }
      if($targets{$id}->[$TARGETS_META]!=$ismeta){
	  $targets{$id}->[$TARGETS_META]=2;
      }

#      print STDOUT "LOCALNODE:\t${id}\n";
    }elsif(exists($target_name_to_id{$full_target_name})){
      $id=$target_name_to_id{$full_target_name};
      $subtargetsnametoid_ref->{$new_target}=$id;

      #possible that same target is referenced relatively/absolutely in various places
      if(not($targets{$id}->[$TARGETS_NAME] eq $new_target)){
	  $targets{$id}->[$TARGETS_NAME]=$new_target;
      }

      #possibly update meta status
      my $ismeta=0;
      if(contains_text($new_target,$makefiles_ref)){#do NOT look at $busy_on_meta_level, as root target would otherwise be falsely recognised as meta
	$ismeta=1;
      }
      if($targets{$id}->[$TARGETS_META]!=$ismeta){
	  $targets{$id}->[$TARGETS_META]=2;
      }

#      print STDOUT "GLOBALNODE:\t${id}\n";
    }else{
      $id=$dummy_target;
    }

  return $id;
}

sub register_target {
    my ($new_target,$subtargetsnametoid_ref,$makefiles_ref,$current_dir_name)=@_;

    my $full_target_name=resolve_target_name($new_target,$current_dir_name);#deal with duplicate targets
    my $id=existing_target($new_target,$subtargetsnametoid_ref,$makefiles_ref,$current_dir_name,$full_target_name);

    if($id eq $dummy_target){
      $id=register_new_target($new_target,$subtargetsnametoid_ref,$makefiles_ref,$current_dir_name,$full_target_name);
    }

    if($debug){
	print STDOUT "<${new_target}> in <${current_dir_name}> yields <${id}>\n";
	my $t=$targets{$id}->[$TARGETS_NAME];
	print STDOUT "<<${t}>> <--> <<${new_target}>>\n";
    }

    return $id;
}

sub register_new_target {
    my ($new_target,$subtargetsnametoid_ref,$makefiles_ref,$current_dir_name,$full_target_name)=@_;

      #first make sure that this target is not accidentally recognized as a makefile include target by deleting it from the list of makefile include targets
#      if(contains_text($new_target,$makefiles_ref)){
#	my $index=0;
	
#	until($makefiles_ref->[$index] eq $new_target){
#	  $index++;
#	}
	
#	delete($makefiles_ref->[$index]);
#      }

#      if($new_target eq "analyze_function.c"){
#	1+5;
#      }

      my $id = create_target_id($new_target);
#      $id='t'.(++($target_count))."_${tmp}";

#      my @payload=();
#      if(contains_text($new_target,$makefiles_ref)){
#	@payload=($new_target,1);
#      }else{
#	@payload=($new_target,0);
#      }

#      $targets{$id}=\@payload;
      $targets{$id}=[];
      $targets{$id}->[$TARGETS_NAME]=$new_target;
      if(contains_text($new_target,$makefiles_ref)){#do NOT look at $busy_on_meta_level, as root target would otherwise be falsely recognised as meta
	$targets{$id}->[$TARGETS_META]=1;
      }else{
	$targets{$id}->[$TARGETS_META]=0;
      }
      $targets{$id}->[$TARGETS_ERROR]=0;

    if($current_dir_name =~ /\/$/){
	$targets{$id}->[$TARGETS_MAKEFILE]=${current_dir_name};
    }else{
	$targets{$id}->[$TARGETS_MAKEFILE]="${current_dir_name}/";
    }

      $targets{$id}->[$TARGETS_LINE]=-1;
      $targets{$id}->[$TARGETS_PHONY]=0;
      $targets{$id}->[$TARGETS_INUSE]=1;
      $targets{$id}->[$TARGETS_COMMANDS]=[];
      $targets{$id}->[$TARGETS_ACTUAL_COMMANDS]=[];
      $targets{$id}->[$TARGETS_TIME]=${node_edge_time}++;
      $targets{$id}->[$TARGETS_DIRNAME]=dirname($full_target_name);
      $targets{$id}->[$TARGETS_BASENAME]=basename($full_target_name);
      $targets{$id}->[$TARGETS_MACROS]=[];
      $subtargetsnametoid_ref->{$new_target}=$id;
      $target_name_to_id{$full_target_name}=$id;

#      print STDOUT "NODE:\t${id}\n";


    return $id;
}

sub register_unused_target {
    my ($new_target,$current_dir_name,$full_target_name)=@_;

      #first make sure that this target is not accidentally recognized as a makefile include target by deleting it from the list of makefile include targets
#      if(contains_text($new_target,$makefiles_ref)){
#	my $index=0;
	
#	until($makefiles_ref->[$index] eq $new_target){
#	  $index++;
#	}
	
#	delete($makefiles_ref->[$index]);
#      }

#      if($new_target eq "analyze_function.c"){
#	1+5;
#      }

#      my $id = create_target_id($new_target);
    my $id=$full_target_name;
#      $id='t'.(++($target_count))."_${tmp}";

#      my @payload=();
#      if(contains_text($new_target,$makefiles_ref)){
#	@payload=($new_target,1);
#      }else{
#	@payload=($new_target,0);
#      }

#      $targets{$id}=\@payload;
    if(not(exists($target_name_to_id{$id})) and not(exists($unused_targets{$id}))){
      $unused_targets{$id}=[];
      $unused_targets{$id}->[$TARGETS_NAME]=$new_target;
      $unused_targets{$id}->[$TARGETS_META]=0;
      $unused_targets{$id}->[$TARGETS_ERROR]=0;

    if($current_dir_name =~ /\/$/){
	$unused_targets{$id}->[$TARGETS_MAKEFILE]=${current_dir_name};
    }else{
	$unused_targets{$id}->[$TARGETS_MAKEFILE]="${current_dir_name}/";
    }

      $unused_targets{$id}->[$TARGETS_LINE]=-1;
      $unused_targets{$id}->[$TARGETS_PHONY]=0;
      $unused_targets{$id}->[$TARGETS_INUSE]=0;
      $unused_targets{$id}->[$TARGETS_COMMANDS]=[];
      $unused_targets{$id}->[$TARGETS_ACTUAL_COMMANDS]=[];
      $unused_targets{$id}->[$TARGETS_TIME]=-1;
      $unused_targets{$id}->[$TARGETS_DIRNAME]=dirname($full_target_name);
      $unused_targets{$id}->[$TARGETS_BASENAME]=basename($full_target_name);
      $unused_targets{$id}->[$TARGETS_MACROS]=[];

      return 1;
    }else{
      return 0;
    }

#      print STDOUT "NODE:\t${id}\n";


#    return $id;
}

#if $parent_target_id is $dummy_target (do not rely on id==0, as meta-targets are also taken into account!), then only target needs to be registered (root of graph!)
sub register_target_and_edge {
  my ($parent_target_id,$dep_name,$dep_dir_name,$subtargetsnametoid_ref,$makefiles_ref,$pruning,$implicit,$is_recursive_make)=@_;

  my $full_target_name=resolve_target_name($dep_name,$dep_dir_name);#deal with duplicate targets
  my $id=existing_target($dep_name,$subtargetsnametoid_ref,$makefiles_ref,$dep_dir_name,$full_target_name);

  if($id eq $dummy_target){

#    unless($parent_target_id eq $dummy_target){
      #problem: edge needs to have timestamp lower than dep, however register_edge needs dep id
      #solution: make up id prior to calling register_edge, and then undo change to ${target_count}
      my $edge=register_edge($parent_target_id,create_target_id($dep_name),$implicit);
      $edges{$edge}->[$EDGES_PRUNING]=$pruning;
      $edges{$edge}->[$EDGES_RECURSIVE]=$is_recursive_make;
      
      --(${target_count});#undo change of ${target_count}
#    }
    
    return register_new_target($dep_name,$subtargetsnametoid_ref,$makefiles_ref,$dep_dir_name,$full_target_name);
  }else{
#    unless($parent_target_id eq $dummy_target){
      #problem: edge needs to have timestamp lower than dep, however register_edge needs dep id
      #solution: make up id prior to calling register_edge, and then undo change to ${target_count}
      my $edge=register_edge($parent_target_id,$id,$implicit);
      $edges{$edge}->[$EDGES_PRUNING]=$pruning;
      $edges{$edge}->[$EDGES_RECURSIVE]=$is_recursive_make;
      return $id;
#      --(${target_count});#undo change of ${target_count}
#    }
  }
}

#Currently double edges possible
sub register_edge {
    my ($node1,$node2,$implicit)=@_;

    my $edge_name='e'.(++($edge_count));

    my $edge_type="0";
    if($busy_on_meta_level){
      $edge_type="1";
    }

    $edges{$edge_name}=[];
    $edges{$edge_name}->[$EDGES_SRC]=$node1;
    $edges{$edge_name}->[$EDGES_DST]=$node2;
    $edges{$edge_name}->[$EDGES_TYPE]=$edge_type;
    $edges{$edge_name}->[$EDGES_TIME]=${node_edge_time}++;
    $edges{$edge_name}->[$EDGES_IMPLICIT]=$implicit;

#    print STDOUT "EDGE:\t${node1} --> ${node2}\n";
    add_edge($node1,$node2);

    return $edge_name;
}

sub create_target_id {
  my ($target_name)=@_;

  my $tmp = make_python_id_of($target_name);
#  if($target_count==0){#first target has its name as id!
#      ++($target_count);
#      return "${tmp}";
#  }else{
  #start_new_make_process takes care of changing name of original target!
  return 't'.(++($target_count))."_${tmp}";
#  }
}

sub make_python_id_of {
  my ($tmp)=@_;

  $tmp =~ s/\./_/g;#replace '.' by '_'
  $tmp =~ s/-/_/g;#replace '-' by '_'
  $tmp =~ s/\+/PLUS/g;#replace '+' by 'PLUS'
  $tmp =~ s/\//_/g;#replace '/' by '_'
  $tmp =~ s/\"/_/g;#replace '"' by '_'
  $tmp =~ s/,/_/g;#replace ',' by '_'
  $tmp =~ s/\@/AT/g;#replace '@' by 'AT'
  $tmp =~ s/ /SPACE/g;#replace ' ' by 'SPACE'

  return $tmp;
}

sub resolve_target_name {
  my ($target_name,$current_dir_name)=@_;

  if($current_dir_name =~ /^(\S+)\/$/){
    $current_dir_name=$1;#get rid of trailing /
  }

  $current_dir_name =~ s/\/+/\//g;#replace // by /
  $target_name =~ s/\/+/\//g;#replace // by /

  if($target_name =~ /^\/.*/){#absolute path
    return $target_name;
  }else{
    #first try to fix problem when for example:
    #$current_dir_name=/home/shane/src/built/src/backend/utils/adt/
    #$target_name=src/backend/utils/adt/numutils.o
    #=> need to transform $target_name into numutils.o
    if($target_name =~ m/^((?:[^\/]+\/)+)([^\/]+)$/){
      my $dir_part=$1;
      my $file_part=$2;
      $dir_part =~ s/\/$//;#remove trailing /

      unless($dir_part =~ /^\./){ #if there is . or .., ignore and use resolution below instead
	if($current_dir_name =~ m/\Q${dir_part}\E$/){
	  my $orig_target_name=$target_name;
	  $target_name=$file_part;#do transformation
	  if($debug){
	    print STDOUT "BUG FIX: ${orig_target_name} => ${target_name}=${dir_part} + ${file_part}\n";
	  }
	}
      }
    }

    my @can=();
    my @path_comps=split(/\//,"${current_dir_name}/${target_name}");
    for (my $i = 0; $i <= $#path_comps; $i++) {
      if ($path_comps[$i] eq '.') {
	;
      } elsif ($path_comps[$i] eq '') {#part before first /
	@can = ();
	push(@can, '');
      } elsif ($path_comps[$i] eq '..') {
	pop(@can);
      } else {
	push(@can, $path_comps[$i]);
      }
    }

    return join('/', @can);
  }
}

sub contains_text {
    my ($token,$list_ref)=@_;

    foreach my $element (@{$list_ref}){
	if(defined($element) and ($element eq $token)){ return 1; }
    }

    return 0;
}

sub add_edge {
  my ($src,$dst)=@_;
  if(exists($edges_src_to_dst{$src})){
    push(@{$edges_src_to_dst{$src}},$dst);
  }else{
    my @tmp=($dst);
    $edges_src_to_dst{$src}=\@tmp;
  }
}

#two ids
sub existing_dependency {
  my ($src,$dst)=@_;
  if(exists($edges_src_to_dst{$src})){
#    print "[TEST] @{$edges_src_to_dst{$src}} --> ${dst}\n";
    return contains_text($dst,$edges_src_to_dst{$src});
  }else{
    return 0;
  }
}

# ===================================================================
# Boilerplating for script...                                       =
# ===================================================================

sub usage_and_exit {
  print STDERR ("Usage: generate_makao_graph.pl [OPTIONS]...\n");
  print STDERR ("Where OPTIONS is one of:\n");
  print STDERR ("  -debug               show debug info\n");
#  print STDERR ("  -debugperf               show debug info for performance\n");
  print STDERR ("  -in IN               read make trace from IN\n");
  print STDERR ("  -out OUT             write graph to OUT\n");
  print STDERR ("  -xml FILE            write target metadata to xml FILE (default: OUT.xml)\n");
  print STDERR ("  -format fileformat   format of generated graph (gdf, vrmlgraph, ncol or prolog)\n");
#  print STDERR ("  -dir DIRNAME  directory from within build has been started\n");
  print STDERR ("  -unused              add unused targets to graph\n");
  print STDERR ("  -quiet               no report at end of run\n");
  print STDERR ("  -version             show version information\n");
  print STDERR ("  -help                print this message\n");
  print STDERR ("\n");
  exit (0);
}

# ===================================================================

sub version_and_exit {
  print STDERR ("This is \"generate_makao_graph.pl\", version ${current_version}.\n");
  print STDERR ("Part of the MAKAO project.\n");
  exit (0);
}




