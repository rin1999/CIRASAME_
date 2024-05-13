#!/bin/bash

for i in 1 2 3 4
do
    cmd="python3 data_format.py --inputfile $1 --outputfiledir $2 --asic $i"
    echo $cmd
    $cmd
done
