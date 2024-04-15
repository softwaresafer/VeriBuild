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

if [ ! $# == 4 ]; then
  echo "Usage: $0 relative_directory concern action prefix with action one of {reset,weave,unweave} and prefix the path prefix used during the original build which will be replaced by the weaving directory prefix."
  exit
fi

DIR=$1
ACTION=$3
PREFIX=$4
ORIG_DIR=$DIR/orig
NEW_DIR=$DIR/makao
WEAVER=$MAKAO/refactoring

cd $WEAVER

WOVEN=$WEAVER/$NEW_DIR/
BASE=$WEAVER/$ORIG_DIR
TOOL=$WEAVER/$DIR/weave-$2.pl

if [ "$ACTION" == reset ]; then
    echo "Resetting..."
    rsync --exclude=".svn" -za $BASE/ $WOVEN    
    exit
fi

echo "Performing ${ACTION}..."
echo "#########################"
perl $TOOL -action $ACTION -debug -in $PREFIX -out $WOVEN
echo "-------------------------"
diff -x ".svn" -r $BASE $WOVEN
echo "#########################"

cd -