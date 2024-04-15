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
# Contributor(s):  Matthias Rieger (matthiasDOTriegerATuaDOTacDOTbe)
#
# ***** END LICENSE BLOCK *****

use strict;
use warnings;
use Getopt::Long;

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
my $format = '';
my $build_dir = '';#directory from within build is started
my @supported_formats=("gdf");#,"vrmlgraph","ncol");
#my $teller=0;

# Process command line options...
GetOptions (
  'help|?' => \$help,
  'version' => \$version,
  'quiet' => \$quiet,
  'debug' => \$debug,
  'in:s' => \$file_in,
  'out:s' => \$file_out,
  'xml:s' => \$xml_out,
  'format:s' => \$format,
  'dir:s' => \$build_dir
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

# Prepare input stream...
if ($file_in) {
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

my $line_count = 0;
my $input = '';
my $last_input_did_match=1;#should only be used in consume*()-methods or with care
my $last_input_was_eof=0;#should only be used in consume*()-methods or with care
my $only_time_prefix="\\s*\\d\\d:\\d\\d:\\d\\d\\s*";
my $time_prefix="\\s*>>>\\s+${only_time_prefix}\\.\\d\\d\\d\\s+\\(clearmake\\):\\s+";

my %edges=();#id -> ref of (node1_id,node2_id)
my $edge_count = 0;

my $EDGES_SRC=0;
my $EDGES_DST=1;
my $EDGES_TYPE=2;
my $EDGES_TIME=3;

my %target_name_to_id=();#targetname -> id
my %targets=();#id -> ref of (targetname,is_meta_dependency,error_code,makefile,line_number,commands_array_ref)
my $target_count = 0;

my $TARGETS_NAME=0;
my $TARGETS_META=1;
my $TARGETS_ERROR=2;
my $TARGETS_MAKEFILE=3;
my $TARGETS_LINE=4;
my $TARGETS_COMMANDS=5;
my $TARGETS_TIME=6;

my %duplicate_to_merged_targets=();

my $dummy_target = "blablabla";
my $error=0;
my $node_edge_time=0;

#my $busy_on_meta_level=0;#true when in cflow of read_makefiles (even if in base part of start_new_make_process in cflow); false otherwise

my $main_target=parse($build_dir,0) or die "Something went horribly wrong on line ${line_count}: <${input}>, stopped...";
close ($HANDLE_IN);

#resolve_duplicates();

if($format eq "gdf"){
    print STDOUT "Generating ${file_out}:\n";

    print STDOUT "\t* writing targets:\t";
    write_gdf_targets($main_target);
    print STDOUT "OK\n";

    print STDOUT "\t* writing edges:\t";
    write_gdf_edges();
    print STDOUT "OK\n";

    print STDOUT "\t* writing XML data:\t";
    write_xml_data($main_target);
    print STDOUT "OK\n";
}elsif($format eq "vrmlgraph"){
    #http://vrmlgraph.i-scream.org.uk/
    print STDOUT "Generating ${file_out}:\n";

    print STDOUT "\t* writing edges:\t";
    write_vrmlgraph_edges();
    print STDOUT "OK\n";

    print STDOUT "\t* writing XML data:\t";
    write_xml_data($main_target);
    print STDOUT "OK\n";
}elsif($format eq "ncol"){
    #http://apropos.icmb.utexas.edu/lgl/
    print STDOUT "Generating ${file_out}:\n";

    print STDOUT "\t* writing edges:\t";
    write_ncol_edges();
    print STDOUT "OK\n";

    print STDOUT "\t* writing XML data:\t";
    write_xml_data($main_target);
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
  print STDERR ("Processed:\n\t* ${line_count} line(s);\n\t* ${edge_count} edge(s);\n\t* ${target_count} target(s).\n");
}

exit(0);


# ===================================================================
# Consume utility methods...                                        =
# ===================================================================


sub getLine() {
  my $line=<$HANDLE_IN>;
  # strange control characters occurring in cmake output: ASCII 27, Hex 1B
  $line =~ s/\x1B//g;
  return $line;
}

sub consume {
    my ($string)=@_;

    if($last_input_did_match){
      $last_input_was_eof=eof($HANDLE_IN);

      if($last_input_was_eof){#currently EOF?
	return 0;
      }else{
	$input=getLine();
	$line_count++;
	
	while(($input =~ /^\s*$/)&&!$last_input_was_eof){#skip whitespace-lines
	  $last_input_was_eof=eof($HANDLE_IN);

	  if($last_input_was_eof){#currently EOF?
	    return 0;
	  }else{
	    $input=getLine();
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
	$input=getLine();
	$line_count++;
	
	while(($input =~ /^\s*$/)&&!$last_input_was_eof){#skip whitespace-lines
	  $last_input_was_eof=eof($HANDLE_IN);

	  if($last_input_was_eof){#currently EOF?
	    return 0;
	  }else{
	    $input=getLine();
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

# ===================================================================
# Parsing...                                                        =
# ===================================================================

sub parse {
  my ($current_dir,$parent_id)=@_;
  my @captures=();

  #>>> 15:53:31.857 (clearmake): Processing description file "Makefile"
  while(consume("${time_prefix}Processing description file.*")){};

  #Processing description file "/vobs/esam/build/release_info/release"
  while(consume("\\s*Processing description file.*")){};

  if(consume_and_capture("\\s*clearmake\\[(\\d+)\\]:\\s+Entering directory\\s+`(\\S+)'\\s*",\@captures)){#clearmake[1]: Entering directory `/vobs/dsl/source02/ConfigDataXml'

    #skip description file dependencies for now
    while(not(consume("\\s*clearmake\\[${captures[0]}\\]:\\s+Leaving directory\\s+`\Q${captures[1]}\E'\\s*"))){
      consume(".*");
    }

    #>>> 16:34:02.310 (clearmake): 
    consume("${time_prefix}\\s*");

    #>>> 16:34:02.310 (clearmake): # --- Active make-related environment variables ---
    consume("${time_prefix}# --- Active make-related environment variables ---.*");

    #>>> 16:34:02.311 (clearmake): #	CCASE_MAKEFLAGS=C gnu -d
    while(consume("${time_prefix}#\\s+.*")){}

    #Processing description file "/vobs/esam/build/release_info/release"
    while(consume("\\s*Processing description file.*")){};
  }

  #>>> 15:54:16.114 (clearmake): Current view is "some_view_name"
  consume("${time_prefix}Current view is \".*\".*");

  #>>> 15:54:16.176 (clearmake): Processing goal target:
  consume("${time_prefix}Processing goal target:.*");

  #	"all"
  @captures=();
  consume_and_capture("\\s*\"(\\S+)\"",\@captures);
  my $target_name=$captures[0];
  my $target_id=register_target_and_edge($parent_id,$target_name,$current_dir);

  #>>> 15:54:16.176 (clearmake): Build evaluating all
  consume("${time_prefix}Build evaluating\\s+\Q${target_name}\E\\s*");

  #>>> 15:54:16.179 (clearmake): Build evaluating  MIJN99.tar
  @captures=();
  while(consume_and_capture("${time_prefix}Build evaluating\\s+(\\S+)\\s*",\@captures)){
    my $dep_name=$captures[0];
    my $dep_id=register_target_and_edge($target_id,$dep_name,$current_dir);

    my @commands=();

    #>>> 15:54:17.341 (clearmake): Build evaluated      FORCE.
    until(consume("${time_prefix}Build evaluated\\s*\Q${dep_name}\E.*")){
      @captures=();

      #Null build script for "FORCE"
      if(consume("\\s*Null build script for \"\Q${dep_name}\E\"\\s*")){
	;
      }elsif(consume("No candidate in current view for \"\Q${dep_name}\E\".*")){#No candidate in current view for "/vobs/dsl/sw/flat/AdamSyst/bibbib_run"
	#>>> 16:41:31.385 (clearmake): Primary dep of "/vobs/esam/objects/eant-a/gHOSTr/vobs/dsl/fsn/app/snmp/bibbib/bibbibtable_PROTMGNT.o" is a non-shareable DO; no point in shopping
	#>>> 15:54:19.518 (clearmake): Shopping for DO named "bibbib_run" in VOB directory "/vobs/dsl/source09/AdamSyst@@"
	consume("${time_prefix}Primary dep of \"\Q${dep_name}\E\" is a non-shareable DO; no point in shopping")
     or consume("${time_prefix}Shopping for DO named \"\\S+\" in VOB directory \"\\S+@@\".*");
	
	#======== Rebuilding "/vobs/dsl/sw/flat/AdamSyst/bibbibco_run" ========
	consume("\\s*======== Rebuilding \"\Q${dep_name}\E\" ========\\s*");
      }elsif(consume_and_capture("${only_time_prefix}\\s+(.*)",\@captures)){
	push(@commands,$captures[0]);
      }elsif(consume("${time_prefix}No derived objects to store.*")){#>>> 15:54:16.304 (clearmake): No derived objects to store
	#========================================================
	consume("========================================================");

	#Successfully rebuilt "MIJN99.tar"
	consume("\\s*Successfully rebuilt \"\Q${dep_name}\E\"\\s*");
      }elsif(consume_and_capture("\\s*clearmake\\[\\d+\\]:\\s+Entering directory\\s+`(\\S+)'\\s*",\@captures)){#clearmake[1]: Entering directory `/vobs/dsl/source02/ConfigDataXml'
	parse($captures[0],$dep_id);
      }else{
	consume(".*");#ignore
      }
    }

    $targets{$dep_id}->[$TARGETS_COMMANDS]=\@commands;

    #>>> 15:54:17.341 (clearmake): `FORCE' is up to date.
    consume("${time_prefix}\\s*`\Q${dep_name}\E' is up to date.*");#sometimes encountered

    @captures=();
  }

  return 1;
}

# ===================================================================
# .gdf generator methods...                                         =
# ===================================================================

sub write_gdf_targets {
  my ($main_target)=@_;
  #  print $HANDLE_OUT "nodedef> name,localname VARCHAR(255),makefile VARCHAR(255),line INT,style,concern VARCHAR(50),ismeta INT,error INT,tstamp INT\n";
  print $HANDLE_OUT "nodedef> name,localname VARCHAR(255),makefile VARCHAR(255),line INT,style,concern VARCHAR(50),error INT,tstamp INT\n";

  for my $key (keys(%targets)){
    my @data=@{$targets{$key}};

    my $concern=$key;
    if ($concern =~ /^.*_(\S*)$/){#use extension as indicator for concern
      $concern=$+;
    }

    my $style=2;
    if($key eq $main_target){
      $style=8;
    }

#    print $HANDLE_OUT "${key},${data[${TARGETS_NAME}]},${data[${TARGETS_MAKEFILE}]},${data[${TARGETS_LINE}]},${style},${concern},${data[${TARGETS_META}]},${data[${TARGETS_ERROR}]},${data[${TARGETS_TIME}]}\n";
    print $HANDLE_OUT "${key},${data[${TARGETS_NAME}]},${data[${TARGETS_MAKEFILE}]},${data[${TARGETS_LINE}]},${style},${concern},${data[${TARGETS_ERROR}]},${data[${TARGETS_TIME}]}\n";
  }
}

sub write_gdf_edges {
#  my %detect_duplicates=();#unneeded, as GUESS can handle it
  print $HANDLE_OUT "edgedef> node1,node2,directed,ismeta INT,tstamp INT\n";

  for my $edge (keys(%edges)) {
    my $src=$edges{$edge}->[$EDGES_SRC];
    my $dst=$edges{$edge}->[$EDGES_DST];
    my $type=$edges{$edge}->[$EDGES_TYPE];
    my $edge_time=$edges{$edge}->[$EDGES_TIME];

 #   if(exists($detect_duplicates{$src})&&($detect_duplicates{$src} eq $dst)){
      #do nothing
#    }els
    if ($src ne $dummy_target){
      # detect duplicates of both $src and $dst and replace them by merged targets
      while(exists($duplicate_to_merged_targets{$src})){
	$src=$duplicate_to_merged_targets{$src};
      }
      while(exists($duplicate_to_merged_targets{$dst})){
	$dst=$duplicate_to_merged_targets{$dst};
      }
      print $HANDLE_OUT "$src,$dst,true,$type,$edge_time\n";
    }else{
      if ($debug){
	print STDERR "!!! Removing virtual edge ($src,$dst)...\n";
      }
      delete($edges{$edge});
      $edge_count--;#no real edge
    }
  }
}

sub write_xml_data {
    my ($main_target)=@_;

    use XML::Writer;
    my $writer = new XML::Writer( OUTPUT => $HANDLE_XML, DATA_MODE => "true", DATA_INDENT => 2 );

    $writer->xmlDecl("UTF-8");
    $writer->startTag("build", "name" => "${main_target}");

    for my $key (keys(%targets)){
	my @commands=@{$targets{$key}->[$TARGETS_COMMANDS]};

	$writer->startTag("target", "name" => "${key}");
	for my $command (@commands){
	    $writer->dataElement("command","$command");
	}
	$writer->endTag();#target
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
# Utility methods...                                                =
# ===================================================================

sub register_target {
    my ($target_name,$current_dir_name)=@_;

    my $id="";

    my $full_target_name=resolve_target_name($target_name,$current_dir_name);#deal with duplicate targets

    if(exists($target_name_to_id{$full_target_name})){
      $id=$target_name_to_id{$full_target_name};
    }else{
      $id=register_new_target($target_name,$current_dir_name,$full_target_name);
    }

    return $id;
}

sub register_new_target {
    my ($target_name,$current_dir_name,$full_target_name)=@_;

    my $id=create_target_id($target_name);

    $targets{$id}=[];
    $targets{$id}->[$TARGETS_NAME]=$target_name;
#      if(contains_text($new_target,$makefiles_ref)){
#	$targets{$id}->[$TARGETS_META]=1;
#      }else{
    $targets{$id}->[$TARGETS_META]=0;
#      }
    $targets{$id}->[$TARGETS_ERROR]=0;
    $targets{$id}->[$TARGETS_MAKEFILE]=${current_dir_name};
    $targets{$id}->[$TARGETS_COMMANDS]=[];
      # $TARGETS_LINE should indicate the line in the make file
      # where a target's rule is located (easy reference to relevant
      # place in makefile). However, in the ClearMake trace no line
      # numbers are mentioned, so this field is useless here.
      # $line_count won't harm.
    $targets{$id}->[$TARGETS_LINE]=$line_count;
    $targets{$id}->[$TARGETS_TIME]=${node_edge_time}++;
    $target_name_to_id{$full_target_name}=$id;

    return $id;
}

#if $parent_target_id is 0, then only target (root of graph!)
sub register_target_and_edge {
  my ($parent_target_id,$dep_name,$dep_dir_name)=@_;

  my $full_target_name=resolve_target_name($dep_name,$dep_dir_name);#deal with duplicate targets
  my $id="";

  if(exists($target_name_to_id{$full_target_name})){
    $id=$target_name_to_id{$full_target_name};
    if($parent_target_id){
      register_edge($parent_target_id,$id);
    }
    #target exists, so do not register
  }else{
    if($parent_target_id){
      #problem: edge needs to have timestamp lower than dep, however register_edge needs dep id
      #solution: make up id prior to calling register_edge, and then undo change to ${target_count}
      register_edge($parent_target_id,create_target_id($dep_name));
      --(${target_count});#undo change of ${target_count}
    }
    $id=register_new_target($dep_name,$dep_dir_name,$full_target_name);
  }

  return $id;
}

#Duplicate edges possible (different timestamp)
sub register_edge {
    my ($node1,$node2)=@_;#two id's!

    my $edge_name='e'.(++($edge_count));

    my $edge_type="0";
#    if($busy_on_meta_level){
#      $edge_type="1";
#    }

    $edges{$edge_name}=[];
    $edges{$edge_name}->[$EDGES_SRC]=$node1;
    $edges{$edge_name}->[$EDGES_DST]=$node2;
    $edges{$edge_name}->[$EDGES_TYPE]=$edge_type;
    $edges{$edge_name}->[$EDGES_TIME]=${node_edge_time}++;

    return $edge_name;
}

sub create_target_id {
  my ($target_name)=@_;

  my $tmp = make_python_id_of($target_name);
  if($target_count==0){#first target has its name as id!
      ++($target_count);
      return "${tmp}";
  }else{
      return 't'.(++($target_count))."_${tmp}";
  }
}

sub make_python_id_of {
  my ($tmp)=@_;

  $tmp =~ s/\./_/g;#replace '.' by '_'
  $tmp =~ s/-/_/g;#replace '-' by '_'
  $tmp =~ s/\+/PLUS/g;#replace '+' by 'PLUS'
  $tmp =~ s/\//_/g;#replace '/' by '_'

  return $tmp;
}

sub resolve_target_name {
  my ($target_name,$current_dir_name)=@_;

  if($current_dir_name =~ /^(\S+)\/$/){
    $current_dir_name=$1;#get rid of trailing /
  }

  if($target_name =~ /\/.*/){#absolute path
    return $target_name;
  }else{
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

# ===================================================================
# Boilerplating for script...                                       =
# ===================================================================

sub usage_and_exit {
  print STDERR ("Usage: generate_makao_graph.clearmake.pl [OPTIONS]...\n");
  print STDERR ("Where OPTIONS is one of:\n");
  print STDERR ("  -debug        show debug info\n");
  print STDERR ("  -in IN        read make trace from IN\n");
  print STDERR ("  -out OUT      write graph to OUT\n");
  print STDERR ("  -xml FILE     write target metadata to xml FILE (default: OUT.xml)\n");
  print STDERR ("  -dir DIRNAME  directory from within build has been started\n");
  print STDERR ("  -quiet        no report at end of run\n");
  print STDERR ("  -version      show version information\n");
  print STDERR ("  -help         print this message\n");
  print STDERR ("\n");
  exit (0);
}

# ===================================================================

sub version_and_exit {
  print STDERR ("This is \"generate_makao_graph.clearmake.pl\", version ${current_version}.\n");
  print STDERR ("Part of the MAKAO project.\n");
  exit (0);
}


