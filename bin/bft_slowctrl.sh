#!/bin/bash

for i in {1..12}
do
echo ./slowctrl.sh $i
./slowctrl.sh $i
done