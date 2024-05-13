#!/bin/bash

dat_path=$1

showPlot="false"

for i in 1 2 3 4
do
outputfilename="test/$2_$i"
args="$dat_path $outputfilename $showPlot"
echo root -l -q -b "fdat2root.C($args)"
root -l -q -b "fdat2root.C($args)"
done