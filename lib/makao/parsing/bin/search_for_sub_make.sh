#!/bin/bash

if [ "$#" -lt "1" ] ; then
  echo "Usage: $0 dir_name"
  exit
fi

DIR=$1

echo "This command searches for all mentions of the word \"make\" in non-source code files."
grep -e "make" -R $DIR | grep -vPe "\.h" | grep -vPe "\.cpp" | grep -vPe "\.py" | grep -vPe "\.java" | grep -vPe "\.class"
