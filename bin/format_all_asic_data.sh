#!/bin/bash
for i in 1 2 3 4
do
echo python3 data_format.py --inputfile $1 --outputfile $2 --asic $i
python3 data_format.py --inputfile $1 --outputfile $2 --asic $i
done