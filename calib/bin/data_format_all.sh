#!/bin/bash

if [$# != 2]; then
    echo usage: ./data_format_all.sh inputfile outputfiledir
    exit 1
else
    for i in 1 2 3 4
    do
        echo data_format.py --inputfile ${1} --outputfiledir ${2} --asic ${i}
        python3 data_format.py --inputfile ${1} --outputfiledir ${2} --asic ${i}
    done
fi