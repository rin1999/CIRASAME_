#!/bin/bash
cirasameid=00000000$1 #number like 01 02 03

echo ../hul-common-lib/install/bin/set_max1932 192.168.2.1${cirasameid: -2} $2
../hul-common-lib/install/bin/set_max1932 192.168.2.1${cirasameid: -2} $2
#echo ../CitirocControlSoft/bin/femcitiroc_control ${cirasameid: -2}
#../CitirocControlSoft/bin/femcitiroc_control -ip=192.168.2.1${cirasameid: -2} -yaml=CIRASAME_calib/yaml_files/cirasame0${cirasameid: -2}/InputDAC.yml -yaml=CIRASAME_calib/yaml_files/cirasame0${cirasameid: -2}/RegisterValue.yml -yaml=CIRASAME_calib/yaml_files/cirasame0${cirasameid: -2}/DiscriMask.yml -sc -read
