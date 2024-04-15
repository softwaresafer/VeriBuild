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

if [ "$#" -lt "2" ] ; then
  echo "$0: need an input prolog file and a target name (optional extra arguments allowed)"
  exit
fi

PROLOG_FILE_NAME=$1
TARGET_NAME=$2

PROJECT_NAME=`echo $PROLOG_FILE_NAME | perl -pe "s/-facts.*.pl//g"`
FACTS_FILE="$PROJECT_NAME-facts.pl"
GDF_FILE="gdf-$PROJECT_NAME*.pl"

shift 2

$MAKAO/filtering/prolog-backward/bin/reduce.sh $FACTS_FILE $GDF_FILE
$MAKAO/filtering/prolog-backward/bin/show.sh out.gdf $TARGET_NAME $@
