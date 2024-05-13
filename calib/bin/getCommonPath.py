#!/usr/bin/env python3
import commonConfigReader
import pprint

config = commonConfigReader.CommonConfigReader()
path_dict = config.readCommonPath()

pprint.pprint(path_dict)

#for x in path_dict:
#    print(f"{x} : {path_dict[x]}")