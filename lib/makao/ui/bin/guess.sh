#!/bin/bash
# adapted from GUESS' guess.sh (http://graphexploration.cond.org/)
# contribution by Reinier Post (http://www.win.tue.nl/~rp/)

CYGWIN=`uname -s | perl -pe "s/^[cC][yY][gG][wW][iI][nN].*$/TRUE/g"`

if [ "$CYGWIN" = "TRUE" ];
then
    ROOT="cygpath -m"
    SEP="\;"
    OPENGL="False"
else
    ROOT="ls"
    SEP=":"
    OPENGL="True"
fi


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

# edit the line below
GUESS_LIB="$GUESS_HOME/lib"
GUESS_CLASSPATH=`${ROOT} $GUESS_LIB/*.jar | paste -s -d${SEP} -`


MAKAO_LIB="$MAKAO/lib"
MAKAO_CLASSPATH=`${ROOT} $MAKAO_LIB/*.jar | paste -s -d${SEP} -`

#JMF_LIB="$JMFHOME/lib"
#JMF_CLASSPATH=`${ROOT} $JMF_LIB/*.jar | paste -s -d${SEP} -`

#SWI_LIB="$SWI/lib"
#SWI_CLASSPATH=`${ROOT} $SWI_LIB/*.jar | paste -s -d${SEP} -`

#echo $GUESS_CLASSPATH${SEP}$MAKAO_CLASSPATH #${SEP}$SWI_CLASSPATH${SEP}$JMF_CLASSPATH

################################################################
# Setup the environment
################################################################
#
#findexe()
#{ oldifs="$IFS"
#  IFS=:
#  for d in $PATH; do
#    if [ -x $d/$1 ]; then
#       IFS="$oldifs"
#       return 0
#    fi
#  done
#  IFS="$oldifs"
#  return 1
#}
#
#for f in swi-prolog swipl pl; do
#  if [ -z "$PL" ]; then
#     if findexe $f; then
#        PL="$f"
#     fi
#  fi
#done
#
#
##needed to obtain installation path of SWI Prolog <--> Windows (non-Cygwin) SWI Prolog generates redundant \r's
#DUMP_OF_VARIABLES=`$PL -dump-runtime-variables | perl -pe "s/\r//g"`
#
#eval $DUMP_OF_VARIABLES
#
#PLLIBDIR=`real_path "$PLBASE/lib/$PLARCH"`
#if [ -z "$LD_LIBRARY_PATH" ]; then
#   LD_LIBRARY_PATH="$PLLIBDIR";
#else
#   LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$PLLIBDIR"
#fi
#
#export LD_LIBRARY_PATH

MAX=2048m
PERM=1024m

export AWT_TOOLKIT=CToolkit
MAKAO_JAVA_HOME=${MAKAO_JAVA_HOME:-${JAVA_HOME}}
if [ "${MAKAO_JAVA_HOME}" == "" ];
then
    echo ""
    echo "*** JAVA_HOME should point to a working Java 6 installation, as MAKAO uses \$JAVA_HOME/bin/java. On OSX, Java 6 typically can be found somewhere under /Library/Java/JavaVirtualMachines/ or /System/Library/Frameworks/JavaVM.framework/Versions/ ***"
    exit
fi

$MAKAO_JAVA_HOME/bin/java -Dsun.java2d.opengl=$OPENGL -Xmx${MAX} -XX:MaxPermSize=${PERM} -DgHome=`real_path $GUESS_HOME` -DMAKAO=`real_path $MAKAO` -classpath $GUESS_CLASSPATH${SEP}$MAKAO_CLASSPATH${SEP}$SWI_CLASSPATH${SEP}$JMF_CLASSPATH -Djava.library.path=`real_path $PLLIBDIR` -Dpython.home=`real_path $MAKAO` -Dpython.path=`real_path $MAKAO`:`real_path $MAKAO/ui/scripts` -Djava.io.tmpdir=`real_path $MAKAO/cachedir` com.hp.hpl.guess.Guess $@

#echo $?
