#!/bin/bash

BIN=~/cirasame/bin/bias_on.sh

for i in {1..18}
do
    COMMAND="$BIN $i $1"
    echo $COMMAND
    $COMMAND
done
