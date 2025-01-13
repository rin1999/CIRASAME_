#!/bin/bash

cirasameid=0000000$1
BIN=~/cirasame/hul-common-lib/install/bin/set_max1932
COMMAND="$BIN 192.168.2.1${cirasameid: -2} 0"
echo $COMMAND
$COMMAND

