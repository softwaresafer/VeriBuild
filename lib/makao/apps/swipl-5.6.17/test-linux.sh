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

BUILD_DIR=/home/bram/Download/pl-5.6.17
PROJECT_DIR=$MAKAO/apps/swipl-5.6.17
FILE_NAME=swi-linux
IN_FILE=$PROJECT_DIR/$FILE_NAME.txt.gz
zcat $IN_FILE > tmpblablabla.txt
IN_FILE=tmpblablabla.txt
OUT_FILE=$PROJECT_DIR/$FILE_NAME.gdf
$MAKAO/parsing/bin/generate_makao_graph.pl -in $IN_FILE -out $OUT_FILE -format gdf  $@
$MAKAO/parsing/bin/find_duplicates.pl -in $OUT_FILE

rm -f $IN_FILE
