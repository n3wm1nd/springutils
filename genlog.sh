#!/bin/bash
for unitfile in *.lua
do
  unitname=${unitfile%.lua}
  unitdesc=$(grep -i "^ *name *=" $unitfile | head -n1 | sed 's/^.*\[\[\(.*\)\]\].*/\1/')
  log=$(git log --no-merges $1 -- $unitfile | sed -e '/^$/d' -e '/^commit /d' -e '/^Date: /d' -e '/^Author: /d')
  if [ -n "$log" ]
  then
    echo "==== $unitname ($unitdesc) ===="
    echo "$log"
    echo 
  fi

done
