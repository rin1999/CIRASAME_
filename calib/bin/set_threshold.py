#!/bin/env python3

import csv
import numpy as np
import pandas as pd
import os
import argparse
import logging
import openpyxl
import shutil

def rewrite_threshold(inputfile: pd.DataFrame, outputfile: dict, cirasameID: int):
    global_asic_list = list(np.arange(start=(cirasameID-1)*4, stop=(cirasameID-1)*4+4))
    print(global_asic_list)
    threshold_list = []
    for global_asic_id in global_asic_list:
        val = inputfile.loc[inputfile['global ASIC number']==global_asic_id]['threshold']
        threshold_list.append(int(val))
    outputfile['CIRASAME Common'].loc[outputfile['CIRASAME Common']['CIRASAME#']==cirasameID, 'Threshold Common 1'] = threshold_list[0]
    outputfile['CIRASAME Common'].loc[outputfile['CIRASAME Common']['CIRASAME#']==cirasameID, 'Threshold Common 2'] = threshold_list[1]
    outputfile['CIRASAME Common'].loc[outputfile['CIRASAME Common']['CIRASAME#']==cirasameID, 'Threshold Common 3'] = threshold_list[2]
    outputfile['CIRASAME Common'].loc[outputfile['CIRASAME Common']['CIRASAME#']==cirasameID, 'Threshold Common 4'] = threshold_list[3]
    #print(outputfile['CIRASAME Common'])

def save_excel(outputfilepath: str, outputfile: dict)->None:
    with pd.ExcelWriter(outputfilepath, engine='openpyxl') as writer:
        for sheet_name, df in outputfile.items():
            pass
            #df.to_excel(writer, sheet_name=sheet_name, index=False)

def main(inputfilepath: str, outputfilepath: str, begin: int, end: int):
    inputfile = pd.read_csv(inputfilepath, header=None, sep='\s+')
    outputfile= pd.read_excel(outputfilepath, sheet_name=None, engine='openpyxl')
    inputfile.columns = ['global ASIC number', '1', '2', 'threshold', '4', '5']
    for cirasameID in range(begin, end+1):
        rewrite_threshold(inputfile, outputfile, cirasameID)
    


if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Read the threshold value from the pulseheightfit_allb out file and save it to an Excel file.")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("-o", "--output", default="~/cirasame/calib/xlsx/cirasame_setting.xlsx", help="Path to the output Excel file (default: output.xlsx)")
    parser.add_argument("-b", "--begin", type=int, default=1)
    parser.add_argument("-e", "--end", type=int, default=12)
    args = parser.parse_args()
    main(args.input_file, args.output, args.begin, args.end)