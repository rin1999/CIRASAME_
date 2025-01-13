#!/usr/bin/env python3

"""
Adjusting inputDAC by using data from biasDAC-adjusted scan.

created : 2024/05/14

NaNが含まれる際に、そのチャンネルのみを無視して処理を続けるように変更

modified: WIP

"""

import os
import numpy as np
import pandas as pd
import cirasameSettingManager
import argparse
from typing import Tuple

#pd.set_option('display.max_rows', None)

CIRASAME_ID_START = 1
CIRASAME_ID_END = 18
CITIROC_START = 1
CITIROC_END = 4
INPUTDAC_REFERENCE = 2.5
OUTFILE_COL_NAME = ['globalID', 'cirasameID', 'citiroc', 'channel', 'gain', 'thresholdDAC', 'baseline']
GAIN_TO_INPUTDAC = 3.806

def save_xlsx(workbook: dict, xlsxfilepath: str) -> None:
    with pd.ExcelWriter(xlsxfilepath, engine='openpyxl') as writer:
        for sheet, dataframe in workbook.items():
            dataframe.to_excel(writer, sheet_name=sheet, index=False)

def get_mean_from_outfile(outfilepath: str, begin_cirasame: int, end_cirasame: int):
    outfile = pd.read_csv(outfilepath, sep='\s+', header=None)
    outfile.columns = OUTFILE_COL_NAME
    gain_mean_all = outfile['gain'][(outfile['gain'] != 0.0) & (outfile['gain'].notna())].mean() #gainがnanだったり0.0の場合を除いた全体の平均
    gain_mean_cirasame = pd.DataFrame(columns=['cirasameID', 'mean_gain'])
    for iCirasame in range(begin_cirasame, end_cirasame+1):
        data = outfile[outfile['cirasameID']==iCirasame]
        mean_gain = data['gain'][(data['gain'] != 0.0) & (data['gain'].notna())].mean()
        #print([iCirasame,mean_gain])
        newrow = pd.DataFrame([[iCirasame, mean_gain]], columns=['cirasameID', 'mean_gain'])
        gain_mean_cirasame = pd.concat([gain_mean_cirasame, newrow], ignore_index=True)
    return gain_mean_all, gain_mean_cirasame, outfile


def calculate_shift(outfilepath: str, begin_cirasame: int, end_cirasame: int)-> pd.DataFrame:
    gain_mean_all, gain_mean_cirasame, outfile = get_mean_from_outfile(outfilepath, begin_cirasame, end_cirasame)
    df_gain_mean = pd.DataFrame(columns=['cirasameID', 'citiroc', 'channel', 'gain_mean'])
    df_gain = pd.DataFrame(columns=['cirasameID', 'citiroc', 'channel', 'gain'])
    for iCirasame in range(begin_cirasame, end_cirasame+1):
        for iCitiroc in range(1, 5):
            for iChannel in range(1, 33):
                newrow_mean = pd.DataFrame([[iCirasame, iCitiroc, iChannel, gain_mean_all]], columns=['cirasameID', 'citiroc', 'channel', 'gain_mean'])
                df_gain_mean = pd.concat([df_gain_mean, newrow_mean], ignore_index=True)
                gain = outfile.loc[(outfile['cirasameID']==iCirasame) & (outfile['citiroc']==iCitiroc) & (outfile['channel']==iChannel), 'gain'].iloc[0]
                newrow = pd.DataFrame([[iCirasame, iCitiroc, iChannel, gain]], columns=['cirasameID', 'citiroc', 'channel', 'gain'])
                df_gain = pd.concat([df_gain, newrow], ignore_index=True)
    series_diff = df_gain['gain'] - df_gain_mean['gain_mean']
    df_gain_shift = df_gain.copy()
    df_gain_shift = df_gain_shift.drop(columns=['gain'])
    df_gain_shift['gain_diff'] = series_diff
    df_gain_shift['shift'] = df_gain_shift['gain_diff'].apply(lambda x: round(-3.806*x))
    return df_gain_shift


def update_xlsx(workbook: dict, df_gain_shift: pd.DataFrame, begin_cirasame: int, end_cirasame: int, xlsxfilepath: str, isExecute: bool):
    for iCirasame in range(begin_cirasame, end_cirasame+1):
        data = df_gain_shift[df_gain_shift['cirasameID']==iCirasame]
        prev_bias = data['shift'].reset_index()
        workbook[f'CIRASAME{iCirasame}']['Bias Individual'] = workbook[f'CIRASAME{iCirasame}']['Bias Individual'] + prev_bias['shift']
        print(f'CIRASAME{iCirasame}-----------------------------------------')
        print(workbook[f'CIRASAME{iCirasame}'])
    if isExecute:
        save_xlsx(workbook, xlsxfilepath)
    else :
        print('Do not forget to run in execute mode')


def main(outfilepath: str, xlsxfilepath:str, isExecute: bool, begin_cirasame: int, end_cirasame: int):
    workbook = pd.read_excel(xlsxfilepath, sheet_name=None, engine='openpyxl')
    df_gain_shift = calculate_shift(outfilepath, begin_cirasame, end_cirasame)
    update_xlsx(workbook, df_gain_shift, begin_cirasame, end_cirasame, xlsxfilepath, isExecute)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outfile', required=True, type=str, help='Path to the *_chan_*.out file')
    parser.add_argument('-e', '--excel', required=True, type=str, help='Path to the .xlsx file used during this scan.')
    parser.add_argument('--begin', default=1, type=int, help='First CIRASAME ID.')
    parser.add_argument('--end', default=18, type=int, help='Final CIRASAME ID.')
    parser.add_argument('-x', '--execute', action='store_true', help="Execute the script.")
    args = parser.parse_args()
    outfilepath = os.path.expanduser(args.outfile)
    xlsxfilepath= os.path.expanduser(args.excel)

    main(outfilepath,xlsxfilepath,args.execute,args.begin, args.end)

