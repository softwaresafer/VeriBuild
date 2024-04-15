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

if [ "$#" -lt "1" ] ; then
  echo "$0: need at least one input data file"
  exit
fi

EXECUTABLE=reduce
RULES=`ls $MAKAO/filtering/prolog-backward/rules/*.pl | paste -s - | perl -pe "s/\S+chore.pl//g"`
#RULES="$MAKAO/rules/prolog/meta.pl $MAKAO/rules/prolog/transitivity.pl $MAKAO/rules/prolog/obsolete.pl $MAKAO/rules/prolog/abstraction.pl $MAKAO/rules/prolog/linux.pl"
#RULES="$MAKAO/rules/prolog/meta.pl"

#SWIPL=`ls $SWI/bin/swipl | perl -pe "s/.*No\s+such\s+file\s+or\s+directory.*/no/"`
#SWIPL=`find $SWI -name "swipl"`

#echo "target: $TARGETFILE"

#find right SWI executable
findexe()
{ oldifs="$IFS"
  IFS=:
  for d in $PATH; do
    if [ -x $d/$1 ]; then
       IFS="$oldifs"
       return 0
    fi
  done
  IFS="$oldifs"
  return 1
}

for f in swi-prolog swipl pl; do
  if [ -z "$PL" ]; then
     if findexe $f; then
        PL="$f"
     fi
  fi
done

$PL -g dump_and_halt -o $EXECUTABLE -c $@ $RULES

#else
#    swipl -g reduce_and_halt\(\'${TARGETFILE}\'\) -o $EXECUTABLE -c $MAKAO/rules/prolog/main.pl $@ $RULES
#fi

./$EXECUTABLE

rm -f $EXECUTABLE