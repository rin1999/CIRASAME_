#!/bin/bash

BIN=~/cirasame/bin/bias_on.sh

for i in {19..21}
do
    COMMAND="$BIN $i $1"
    echo $COMMAND
    $COMMAND
done
