#!/bin/bash

for i in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18
do
    cmd="./format_all_asic_data.sh cirasame0${i}_$1 thresholdscan_$1"
    echo $cmd
    $cmd
done
