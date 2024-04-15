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
) or usage_and_exit ();

# Show help if requested...
if ($help) { usage_and_exit (); }

# Show version info if requested...
if ($version) { version_and_exit (); }


# ===================================================================
# Prepare I/O streams...                                            =
# ===================================================================
my $HANDLE_IN;

# Prepare input stream...
if ($file_in) {
    open ($HANDLE_IN, $file_in) or die "Input file ${file_in} could not be found!";
}else{
    die "No input file specified!";
}

# ===================================================================
# Main logic...                                                     =
# ===================================================================

my $line_count = 0;
my $input = '';
my $last_input_did_match=1;#should only be used in consume*()-methods or with care
my $last_input_was_eof=0;#should only be used in consume*()-methods or with care
my $only_time_prefix="\\s*\\d\\d:\\d\\d:\\d\\d\\s*";
my $time_prefix="\\s*>>>\\s+${only_time_prefix}\\.\\d\\d\\d\\s+\\(clearmake\\):\\s+";

my %duplicate_canonicalised_target_name_to_array_of_line_numbers=();#name -> ref of [[makefile_nr,gdf_nr],[makefile_nr,gdf_nr],...]

my $dummy_target = "blablabla";
my $error=0;
my $node_edge_time=0;

process(\%duplicate_canonicalised_target_name_to_array_of_line_numbers) or die "Something went horribly wrong on line ${line_count}: <${input}>, stopped...";
detect_violations(\%duplicate_canonicalised_target_name_to_array_of_line_numbers);
close ($HANDLE_IN);

# ===================================================================
# Endgame...                                                        =
# ===================================================================

if (!$quiet) {
    my $nr_of_distinct_targets=keys(%duplicate_canonicalised_target_name_to_array_of_line_numbers);
    $line_count=$line_count-2;#make up for the nodedef- and edgedef-lines!
    my $nr_of_redundant_targets=$line_count-$nr_of_distinct_targets;
    print STDERR ("Duplicate detection:\n\t* ${line_count} line(s);\n\t* ${nr_of_distinct_targets} distinct target(s);\n\t* ${nr_of_redundant_targets} redundant target(s).\n");
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

sub process {
  my ($duplicate_canonicalised_target_name_to_array_of_line_numbers_ref)=@_;
  my @captures=();

  #nodedef> name,localname VARCHAR(255),makefile VARCHAR(255),line INT,style,concern VARCHAR(50),error INT,tstamp INT,phony INT,path VARCHAR(255)
  consume("nodedef>\\s+.*");

  #t19_GnuCLexer_java,GnuCLexer.java,/home/bram/workspace/svn/aspicere/trunk/cgram/grammars/Makefile,21,2,java,0,40,1,/home/bram/workspace/svn/aspicere/trunk/cgram/grammars,GnuCLexer.java,1
  while(consume_and_capture("^\\S+,(\\S+),(\\S+),(\-??\\d+),\\d+,\\S*,\-??\\d+,\-??\\d+,[01],(\\S+),(\\S+),[01]",\@captures)){
      if($debug){
	  print STDOUT "DEBUG: @{captures}\n";
	  print STDOUT "BEFORE: ${captures[1]}\n";
      }

      if($captures[1] =~ /^(\S+)\/$/){
	  #OK
      }else{
	  my @path_comps=split(/\//,"${captures[1]}");
	  pop(@path_comps);#get rid of Makefile if any
	  $captures[1]=join('/',@path_comps);
      }

      if($debug){
	  print STDOUT "AFTER: ${captures[1]}\n";
      }

      #my $full_target_name=resolve_target_name($captures[0],$captures[1]);
      my $full_target_name="${captures[3]}/${captures[4]}";
      #($full_target_name eq $captures[3]) or die "Wrong full target name check: ${full_target_name} <--> ${captures[3]}";
      add_key_value_pair($duplicate_canonicalised_target_name_to_array_of_line_numbers_ref,$full_target_name,$captures[2]);
      @captures=();
  }

  #edges do not need to be processed, but we need to be sure that all nodes were processed!
  ($input =~ /edgedef>\s+.*/) or die "Error while processing on line ${line_count}: ${input}";

  return 1;
}

sub detect_violations {
    my ($duplicate_canonicalised_target_name_to_array_of_line_numbers_ref)=@_;

    for my $key (keys(%{$duplicate_canonicalised_target_name_to_array_of_line_numbers_ref})){
	my $nr_of_lines=@{$duplicate_canonicalised_target_name_to_array_of_line_numbers_ref->{$key}};
	if($nr_of_lines>1){
	    print STDOUT "[${key}]\t\n";
	    for my $element (@{$duplicate_canonicalised_target_name_to_array_of_line_numbers_ref->{$key}}){
		print STDOUT "\t$element->[0] on line $element->[1]\n";
	    }
	    print STDOUT "\n";	    
	}
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

  $current_dir_name =~ s/\/+/\//g;#replace // by /
  $target_name =~ s/\/+/\//g;#replace // by /

  if($target_name =~ /^\/.*/){#absolute path
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

sub add_key_value_pair {
    my ($map_ref,$key,$value)=@_;

    my @tmp=($value,$line_count);

    if(exists($map_ref->{$key})){
	push(@{$map_ref->{$key}},\@tmp);
    }else{
	$map_ref->{$key}=[\@tmp];
    }
}

# ===================================================================
# Boilerplating for script...                                       =
# ===================================================================

sub usage_and_exit {
  print STDERR ("Usage: find_duplicates.pl [OPTIONS]...\n");
  print STDERR ("Where OPTIONS is one of:\n");
  print STDERR ("  -debug        show debug info\n");
  print STDERR ("  -in IN        read GUESS graph from IN\n");
  print STDERR ("  -quiet        no report at end of run\n");
  print STDERR ("  -version      show version information\n");
  print STDERR ("  -help         print this message\n");
  print STDERR ("\n");
  exit (0);
}

# ===================================================================

sub version_and_exit {
  print STDERR ("This is \"find_duplicates.pl\", version ${current_version}.\n");
  print STDERR ("Part of the MAKAO project.\n");
  exit (0);
}


