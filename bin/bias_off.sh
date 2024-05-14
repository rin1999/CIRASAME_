#!/bin/bash

cirasameid=0000000$1

echo ../hul-common-lib/install/bin/set_max1932 192.168.2.1${cirasameid: -2} 0
../hul-common-lib/install/bin/set_max1932 192.168.2.1${cirasameid: -2} 0
