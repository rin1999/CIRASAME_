#!/bin/bash
for i in {13..18}
do
echo ./bias_on.sh $i $1
./bias_on.sh $i $1
done