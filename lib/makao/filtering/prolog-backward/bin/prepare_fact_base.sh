#!/bin/bash

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

WORK_DIR=$MAKAO/filtering/prolog-backward/experiments/linux-2.6.0
TRACE_FILE=$MAKAO/apps/linux/linux-2.6.0-vmlinux.txt
PL_IN=$WORK_DIR/linux-facts.pl
PL_OUT=$WORK_DIR/facts.pl

$MAKAO/parsing/bin/generate_makao_graph.pl -in $TRACE_FILE -out $PL_IN -format prolog
$MAKAO/filtering/prolog-backward/bin/remove_duplicate_lines.pl -in $PL_IN -out $PL_OUT
mv $PL_OUT $PL_IN
