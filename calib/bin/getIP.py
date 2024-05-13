#!/usr/bin/env python3
import argparse
import commonConfigReader

parser = argparse.ArgumentParser()
parser.add_argument("-id", "--cirasameID", required=True)
args = parser.parse_args()

id = int(args.cirasameID)

config = commonConfigReader.CommonConfigReader()
ip = config.readCirasameIP(id)

print(ip)