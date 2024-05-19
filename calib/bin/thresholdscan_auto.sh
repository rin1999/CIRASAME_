#!/bin/bash

# Check if both beginning and end arguments are provided
if [ $# -ne 4 ]; then
    echo "Usage: $0 <nparallel> <begin> <end> <run name>"
    echo "   nparallel: the number of processes that run in parallel. 3 recommende."
    echo "   begin: the first CIRASAME number of the iteraction"
    echo "   end: the last CIRASAME number of the iteration"
    echo "   run name: unique name of the scan. Recommended: YYYYDDMM_HHmm"
    echo "   e.g. "
    echo "     ~/cirasame/calib> bin/thresholdscan_auto.sh 3 1 12 20240422_0130"
    echo ""
    exit 1
fi
nparallel=$1
begin=$2
end=$3
runname=$4

command="./thresholdscan_single.py"

cd ~/cirasame/calib/bin
for ((i = begin; i <= end; i++)); do
#    arg="-n cirasame$(printf "%03d" $i)_$runname -s yml/cirasame$(printf "%03d" $i)/settings.yml"
    arg="-r $runname -n $i"
    printf "%s\n" "$arg"
done | xargs -n 1 -P $nparallel -I {} sh -c "$command {}"

echo "All commands have completed."
./attentionplease.sh
