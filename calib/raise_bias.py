'''
raising bias from 255 to disignated value

tracks 2 CIRASAMEs
'''

import os
import sys
import time
import yaml
import argparse
import subprocess as sub
import numpy as np
import matplotlib.pyplot as plt

hul_path = '../hul-common-lib/install/bin'

parser = argparse.ArgumentParser()
parser.add_argument('-f','--filelist', required=True, nargs='*', type=int, help='lsit of CIRASAME ID')
args = parser.parse_args()

file_list = args.filelist

