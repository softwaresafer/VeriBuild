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
#        Reinier Post (http://www.win.tue.nl/~rp/)
#
# ***** END LICENSE BLOCK *****

#first argument: .gdf
#second argument: targetname
ARGS=1

if [ $# -lt "$ARGS" ]
# Correct number of arguments passed to script?
then
  echo "Usage: `basename $0` filename"
  exit 1
fi

FILE_NAME=$1
shift 1

CYGWIN=`uname -s | perl -pe "s/^[cC][yY][gG][wW][iI][nN].*$/TRUE/g"`

function real_path {
   RES="$@"

   if [ "$CYGWIN" = "TRUE" ];
   then
       if [ -z "$RES" ]
       then
	   :
       else
	   cygpath -m "$RES"
       fi
   else
       echo $RES
   fi  

}

TMPFILE=tmp-`date "+%H_%M_%S"`.py
PREFUSE=`echo " $@ " | perl -pe "s/.*\s+--prefuse\s+.*/yes/" | perl -pe "s/.*\s+-p\s+.*/yes/"`
if [ "$PREFUSE" == "yes" ]; then
    echo "prefuse=1" > $TMPFILE
else
    echo "prefuse=0" > $TMPFILE
fi

MAKAO_REAL=`real_path $MAKAO`
echo "makao_path=\"$MAKAO_REAL/\"" >> $TMPFILE

CRYSTAL_REAL=`real_path $CRYSTAL`
echo "crystal_path=\"$CRYSTAL_REAL/\"" >> $TMPFILE

HULLS=`echo " $@ " | perl -pe "s/.*\s+--hulls\s+.*/yes/"`
if [ "$HULLS" == "yes" ]; then
    echo "enable_hulls=1" >> $TMPFILE
else
    echo "enable_hulls=0" >> $TMPFILE
fi

GDF=`echo " $FILE_NAME " | perl -pe "s/.*\.gdf\s*$/yes/"`
FILE_NAME_REAL=`real_path $FILE_NAME`
FILE_DIR_NAME=`dirname $FILE_NAME_REAL`
FILE_BASE_NAME=`basename $FILE_NAME_REAL`
if [ "$GDF" == "yes" ]; then
    echo "gdf_dir_name=\"$FILE_DIR_NAME/\"" >> $TMPFILE
    echo "gdf_file_name=\"$FILE_BASE_NAME\"" >> $TMPFILE
else
    echo "gdf_dir_name=\"$FILE_DIR_NAME/../\"" >> $TMPFILE
    echo "gdf_file_name=\"$FILE_BASE_NAME.gdf\"" >> $TMPFILE
fi

#not standard argument of guess.sh
ACTUAL_ARGS=`echo " $@ " | perl -pe "s/--hulls//g"`

MARKER_FILE=${FILE_DIR_NAME}/save_marker.bla
rm -f $MARKER_FILE

MAIN_SCRIPT="$MAKAO/ui/scripts/makao.py"
OTHER_MAIN_SCRIPT=`echo " $@ " | perl -pe "s/.*\s+--load\s+(\S+)\s*.*/yes/"`
if [ "$OTHER_MAIN_SCRIPT" == "yes" ]; then
    MAIN_SCRIPT=`echo " $@ " | perl -pe "s/^.*\s+--load\s+(\S+)\s*.*$/\1/"`
    ACTUAL_ARGS=`echo " $ACTUAL_ARGS " | perl -pe "s/--load\s+(\S+)//g"`
fi

echo "$MAKAO/ui/bin/guess.sh -m `real_path $FILE_NAME` `real_path $TMPFILE` `real_path $MAIN_SCRIPT` $ACTUAL_ARGS"
$MAKAO/ui/bin/guess.sh -m `real_path $FILE_NAME` `real_path $TMPFILE` `real_path $MAIN_SCRIPT` $ACTUAL_ARGS
rm -f $TMPFILE

if [ "$PREFUSE" == "yes" ]; then

    if [ -f "$MARKER_FILE" ]; then
	#OK, we just exited Prefuse and the user wants to open the exported graph in Piccolo frontend
	PICCOLO_GRAPH=`head -n 1 ${MARKER_FILE}`
	NEW_ARGS=`echo " $@ " | perl -pe "s/.*\s+--prefuse\s+.*//" | perl -pe "s/.*\s+-p\s+.*//"`
	    
	echo ""
	echo "[ANALYSIS STARTING] opening ${PICCOLO_GRAPH} ..."
	echo ""
	$0 $PICCOLO_GRAPH $NEW_ARGS	
    fi
fi

rm -f $MARKER_FILE
