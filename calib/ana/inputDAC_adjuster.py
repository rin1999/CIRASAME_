#!/usr/bin/env python3

"""
Adjusting inputDAC by using data from biasDAC-adjusted scan.


created : 2024/05/14
"""

import os
import numpy as np
import pandas as pd
import cirasameSettingManager
import matplotlib.pyplot as plt
import argparse
from typing import Tuple

CIRASAME_ID_START = 1
CIRASAME_ID_END = 18
CITIROC_START = 1
CITIROC_END = 4
INPUTDAC_REFERENCE = 2.5
OUTFILE_COL_NAME = ['globalID', 'cirasameID', 'citiroc', 'channel', 'gain', 'thresholdDAC', 'baseline']
GAIN_TO_INPUTDAC = 3.806

def rewrite_xlsx(workbook: dict, xlsxfilepath: str) -> None:
    with pd.ExcelWriter(xlsxfilepath, engine='openpyxl') as writer:
        for sheet, dataframe in workbook.items():
            dataframe.to_excel(writer, sheet_name=sheet, index=False)

def get_xlsx(xlsxfilepath: str) -> dict:
    data = pd.read_excel(xlsxfilepath, sheet_name=None, engine='openpyxl')
    return data

def get_outfile(outfilepath: str) -> Tuple[dict,float]:
    data = pd.read_csv(outfilepath, sep='\s+', header=None)
    data.columns = OUTFILE_COL_NAME
    gain_mean_all = data['gain'].mean(skipna=True)
    data_dict = {}
    for i_cirasame in range(CIRASAME_ID_START, CIRASAME_ID_END+1):
        data_dict[f'CIRASAME{i_cirasame}'] = data[data['cirasameID']==i_cirasame]
    return data_dict , gain_mean_all

def shift_inputDAC(inputDAC_series: pd.Series, gain_series: pd.Series, gain_mean_cirasame: float) -> pd.Series:
    gain_series = gain_series.fillna(gain_mean_cirasame)
    gain_series = gain_series.mask((gain_series <= gain_mean_cirasame-10) & (gain_mean_cirasame+10 <= gain_series), gain_mean_cirasame)
    gain_diff_series = gain_series - gain_mean_cirasame
    print(f"mean_cirasame = {gain_mean_cirasame}")
    print(f"gain_diff mean = {gain_diff_series.mean()}")
    #if gain_diff_series.mean() != 0.0:
    #    print(gain_diff_series.to_list())
    inputDAC_list = []
    for inputDAC, gain_diff in zip(inputDAC_series.to_list(), gain_diff_series.to_list()):
        inputDAC_list.append(int(inputDAC - GAIN_TO_INPUTDAC*gain_diff))
        
    inputDAC_series_return = pd.Series(inputDAC_list)
    return inputDAC_series_return


def loop_process(workbook: dict, out: dict, i_cirasame: int, gain_mean_all: float) -> dict:
    print(f'processing cirasame{i_cirasame}')
    sheetname = f'CIRASAME{i_cirasame}'
    inputDAC_series = workbook[sheetname]['Bias Individual']
    gain_series = out[sheetname]['gain']
    gain_mean_cirasame = gain_series.dropna().loc[(gain_series >= gain_mean_all-20) & (gain_series <= gain_mean_all+20)].mean()
    inputDAC_series_shifted = shift_inputDAC(inputDAC_series, gain_series, gain_mean_cirasame)
    workbook[sheetname]['Bias Individual'] = inputDAC_series_shifted

    #print(f"gain of cirasame{i_cirasame} = {gain_series}")
    #print(f"shifted inputDAC cirasame{i_cirasame} = {inputDAC_series_shifted}")

    return workbook


def main(outfilepath: str, xlsxfilepath:str, isExecute: bool):
    workbook           = get_xlsx(xlsxfilepath)
    out, gain_mean_all = get_outfile(outfilepath)
    print(f"mean_all = {gain_mean_all}")
    for i_cirasame in range(CIRASAME_ID_START, CIRASAME_ID_END+1):
        workbook = loop_process(workbook, out, i_cirasame, gain_mean_all)

    if isExecute:
        rewrite_xlsx(workbook, xlsxfilepath)

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outfile', required=True, type=str, help='your out file path here')
    parser.add_argument('-e', '--excel', required=True, type=str, help='your xlsx file path here')
    parser.add_argument('-x', '--execute', action='store_true', help="Execute the script (default: dry run)")
    #parser.add_argument('-m', '--mode', required=True, type=str, choices=["ID", "ASIC"], help='(ID :use average gain of cirasame and adjust ID indivisually) (ASIC :use average gain of cirasame and adjust citiroc)')
    args = parser.parse_args()
    outfilepath = os.path.expanduser(args.outfile)
    xlsxfilepath= os.path.expanduser(args.excel)

    main(outfilepath,xlsxfilepath,args.execute)
