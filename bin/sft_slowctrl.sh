#!/bin/bash

for i in {13..18}
do
echo ./slowctrl.sh $i
./slowctrl.sh $i
done