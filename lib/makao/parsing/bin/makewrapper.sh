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
  echo "Usage: $0 target_name"
  echo ""
  echo "=> Specify #make processes (default: 1) using: NRJ=4 $0 target_name"
  echo "=> Specify timing command (default: none) using: TIMH=/usr/bin/time $0 target_name"
  exit
fi

TARGET=$1

NRJ=${NRJ:-1}
TIMH=${TIMH:-}
MAKE=${MAKE:-make}

OLD_SHELL=$SHELL

#quoting!!!
SHELL_QUOTED=`echo "${TIMH} ${OLD_SHELL} -o xtrace" | sed 's/ /\\\\ /g'`
export SHELL=${TIMH}\ ${OLD_SHELL}\ -o\ xtrace
export CONFIG_SHELL=${TIMH}\ ${OLD_SHELL}\ -o\ xtrace
#make -w --debug=v --debug=m -p SHELL:="${SHELL}" CONFIG_SHELL:="${SHELL}" MAKEFLAGS="-w --debug=v --debug=m -p SHELL:=${SHELL_QUOTED}" MAKE="make -w --debug=v --debug=m -p SHELL:=${SHELL_QUOTED}" $TARGET
#MAKEFLAGS is automatically set by GNU Make!
${MAKE} -j "${NRJ}" -w --debug=v --debug=m -p SHELL:="${SHELL}" CONFIG_SHELL:="${SHELL}" MAKE="${MAKE} -w --debug=v --debug=m -p SHELL:=${SHELL_QUOTED}" $TARGET
