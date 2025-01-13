#!/bin/bash

cirasameid=00000000$1

yaml_dir=~/cirasame/calib/config/cirasame0${cirasameid: -2}
exec_dir=~/cirasame/CitirocControlSoft/bin
exec_bin="$exec_dir/femcitiroc_control"
exec_arg_ip="-ip=192.168.2.1${cirasameid: -2}"
exec_arg_yaml="-yaml=$yaml_dir/DiscriMask.yml -yaml=$yaml_dir/InputDAC.yml -yaml=$yaml_dir/RegisterValue.yml"
exec_arg_other="-sc -read" 

exec_cmd="$exec_bin $exec_arg_ip $exec_arg_yaml $exec_arg_other"

echo $exec_cmd
$exec_cmd
