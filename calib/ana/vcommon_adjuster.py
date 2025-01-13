#!/usr/bin/env python3

"""
calculate and change biasDAC by using gain data 

.outにnanが書かれたCIRASAMEは調整対象としていない
例：
cirasame001~018の内、002のデータのみがnanだった場合、
002以外のV_commonが調節される。

created : 2024/10/14 - not ready
"""

import os
import numpy as np
import pandas as pd
import argparse


def read_outfile(filepath: str):
    col_name = ['cirasameID','gain']
    df = pd.read_csv(filepath, sep='\s+', header=None)
    df.columns=col_name
    cirasameID_list = df['cirasameID'].to_list()
    # the behaviour of dropna is not optimal as it really "drops" it
    # rather than replacing it with 0. 
    gain = df['gain']
    return cirasameID_list, gain

def update_xlsx(filepath: str, cirasameID_list: list, bias_shift: pd.Series, isExecute: bool) -> None:
    workbook = pd.read_excel(filepath, sheet_name=None, engine='openpyxl')
    #print('Bias Common column in xlsx sheet:')
    #print(workbook['CIRASAME Common']['Bias Common'])
    workbook['CIRASAME Common']['Bias Common'] = workbook['CIRASAME Common']['Bias Common'] + bias_shift.fillna(0).astype(int)
    print('Bias Common column in xlsx sheet (after adjustment):')
    print(workbook['CIRASAME Common']['Bias Common'])
    if isExecute:
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet, dataframe in workbook.items():
                dataframe.to_excel(writer, sheet_name=sheet, index=False)
    else:
        print('Do not forget to run in execute mode!!!')

def calculate_bias_shift(gain_prev: pd.Series) -> pd.Series:
    gain_average = gain_prev.mean(skipna=True)
    bias_shift = gain_prev.apply(lambda x: round((x-gain_average)/3.68) if pd.notna(x) else x) 
    return bias_shift

def main(filepath: str, xlsxpath: str, isExecute: bool):
    cirasameID_list, gain_prev = read_outfile(filepath)
    bias_shift = calculate_bias_shift(gain_prev)
    print(f"Vcommon shift is:\n{bias_shift}")
    update_xlsx(xlsxpath, cirasameID_list, bias_shift, isExecute)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outfile', required=True, type=str, help='your crsm out file path here (use outfiles with crsm in filename)')
    parser.add_argument('-e', '--excel', required=True, type=str, help='your xlsx file path here')
    parser.add_argument('-x', '--execute', action='store_true', help='Execute the script (default: dry run)')
    args = parser.parse_args()
    filepath = os.path.expanduser(args.outfile)
    xlsxpath = os.path.expanduser(args.excel)
    isExecute= args.execute
    main(filepath, xlsxpath, isExecute)
