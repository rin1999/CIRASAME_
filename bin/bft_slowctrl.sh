#!/bin/bash

for i in {1..18}
do
echo ./slowctrl.sh $i
./slowctrl.sh $i
done
