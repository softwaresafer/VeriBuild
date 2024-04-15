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

# Process command line options...
GetOptions (
  'help|?' => \$help,
  'version' => \$version,
  'quiet' => \$quiet,
  'in:s' => \$file_in,
  'out:s' => \$file_out
) or usage_and_exit ();

# Show help if requested...
if ($help) { usage_and_exit (); }

# Show version info if requested...
if ($version) { version_and_exit (); }


# ===================================================================
# Prepare I/O streams...                                            =
# ===================================================================

# Prepare input stream...
my $HANDLE_IN;
if ($file_in) {
    open ($HANDLE_IN, $file_in) or die "Input file ${file_in} could not be found!";
}else{
    die "No input file specified!";
}

# Prepare output stream...
my $HANDLE_OUT;
if ($file_out) {
    open ($HANDLE_OUT, ">$file_out") or die "Output file ${file_out} could not be opened!";
}else{
    die "No output file specified!";
}

# ===================================================================
# Main logic...                                                     =
# ===================================================================

my %seen;

my $duplicate_count = 0;
while(<$HANDLE_IN>) {
	if ($seen{$_}) {
		print STDOUT ("[REMOVED] $_") unless $quiet;
		$duplicate_count++;
		
	} else {
		$seen{$_} = 1;
		print $HANDLE_OUT ($_);
	}
}


# ===================================================================
# Endgame...                                                        =
# ===================================================================

close ($HANDLE_OUT);
close ($HANDLE_IN);

if (!$quiet) {
	print STDOUT ("Removed $duplicate_count duplicate line(s).\n")
}

exit(0);


# ===================================================================
# Boilerplating for script...                                       =
# ===================================================================

sub usage_and_exit {
  print STDERR ("Usage: remove_duplicate_lines.pl [OPTIONS]...\n");
  print STDERR ("Where OPTIONS are:\n");
  print STDERR ("  -debug        show debug info\n");
  print STDERR ("  -in <file>    file to read\n");
  print STDERR ("  -out <file>   file to write\n");
  print STDERR ("  -quiet        no report at end of run\n");
  print STDERR ("  -version      show version information\n");
  print STDERR ("  -help         print this message\n");
  print STDERR ("\n");
  exit (0);
}

# ===================================================================

sub version_and_exit {
  print STDERR ("This is \"remove_duplicate_lines.pl\", version ${current_version}.\n");
  print STDERR ("Part of the MAKAO project.\n");
  exit (0);
}


