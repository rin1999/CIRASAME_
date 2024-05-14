#!/bin/bash
for i in {1..12}
do
echo ./bias_on.sh $i $1
./bias_on.sh $i $1
done