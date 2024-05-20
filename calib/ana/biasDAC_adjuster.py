#!/usr/bin/env python3

"""
calculate and change biasDAC by using gain data 

created : 2024/05/14 - not ready
"""

import os
import numpy as np
import pandas as pd
import argparse


def read_outfile(filepath: str):
    col_name = ['cirasameID','bias']
    df = pd.read_csv(filepath, sep='\s+', header=None)
    df.columns=col_name
    cirasameID_list = df['cirasameID'].to_list()
    gain_list = df['bias'].to_list()
    return cirasameID_list, gain_list

def update_xlsx(filepath: str, cirasameID_list: list, bias_shift: list) -> None:
    sheet = pd.read_excel(filepath, sheet_name='CIRASAME Common', engine='openpyxl')
    print(sheet)
    for id, shift in zip(cirasameID_list, bias_shift):
        print(f'crsmID:{id}   bias_shift:{shift}')
        bias_prev = sheet.at[sheet[sheet['CIRASAME#']==id].index[0], 'Bias Common']
        bias_after= bias_prev + pd.Series(bias_shift)
        print(f'\t biasDAC:{bias_after}')

def calculate_bias_shift(gain_prev: list) -> list:
    gain_average = np.mean(gain_prev)
    gain_diff_biasDAC = (gain_prev-gain_average)/3.68
    bias_shift = list(map(int, gain_diff_biasDAC))
    return bias_shift

def main(filepath: str, xlsxpath: str, isExecute: bool):
    cirasameID_list, gain_prev = read_outfile(filepath)
    bias_shift = calculate_bias_shift(gain_prev)
    if isExecute:
        update_xlsx(xlsxpath, cirasameID_list, bias_shift)
    else:
        print('Bias shift will be')
        print(bias_shift)
        print('Do not forget to run in execute mode')


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outfile', required=True, type=str, help='your crsm out file path here')
    parser.add_argument('-e', '--excel', required=True, type=str, help='your xlsx file path here')
    parser.add_argument('-x', '--execute', action='store_true', help="Execute the script (default: dry run)")
    args = parser.parse_args()
    filepath = os.path.expanduser(args.outfile)
    xlsxpath = os.path.expanduser(args.excel)
    isExecute= args.execute
    main(filepath, xlsxpath, isExecute)