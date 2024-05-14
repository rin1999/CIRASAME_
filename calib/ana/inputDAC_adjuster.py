#!/usr/bin/env python3

import os
import numpy as np
import pandas as pd
import cirasameSettingManager

CIRASAME_ID_START = 1
CIRASAME_ID_END = 2
FILE_PATH = os.path.expanduser("~/cirasame/calib/ana/out/pulseheightfit_all_20240424_2300.out")
EXCEL_PATH= os.path.expanduser("~/cirasame/calib/xlsx/test.xlsx")
INPUTDAC_REFERENCE = 2.5

def dataframe_extract(df: pd.DataFrame, cirasameID: int):
    cirasame_df = df.loc[df['cirasameID']==float(cirasameID)]   # extracting dataframe
    average_gain = cirasame_df['gain'].mean(skipna=True)        # average value of gain
    stddev  = cirasame_df['gain'].std(skipna=True)              # stddev  value of gain
    average_thresholdDAC = cirasame_df['thresholdDAC'].mean(skipna=True)
    average_baseline = cirasame_df['baseline'].mean(skipna=True)
    cirasame_df['gain'].fillna(average_gain, inplace=True)
    cirasame_df['thresholdDAC'].fillna(average_thresholdDAC, inplace=True)
    cirasame_df['baseline'].fillna(average_baseline, inplace=True)
    return cirasame_df, average_gain

def calculate_inputDAC_shift(gain_delta: list) -> list:
    thresholdDAC2volt = 0.0022
    inputDAC_shift = []
    for x in gain_delta:
        gain_delta_volt = thresholdDAC2volt*x
        shift_inputDAC_volt = 10.3*gain_delta_volt
        shift_inputDAC = shift_inputDAC_volt*256/INPUTDAC_REFERENCE
        inputDAC_shift.append(int(-shift_inputDAC))
    return inputDAC_shift


def main():

    column = ['globalID', 'cirasameID', 'citiroc', 'channel', 'gain', 'thresholdDAC', 'baseline']
    df = pd.read_csv(FILE_PATH, sep="\s+", dtype=float, header=None)
    df.columns = column
    pd.set_option('display.max_rows', 900)
    excel_df_dict = pd.read_excel(EXCEL_PATH, engine='openpyxl', sheet_name=None)   # loading excel book
    
    # loop for each cirasame
    for cirasameID in range(CIRASAME_ID_START,CIRASAME_ID_END+1):    
        print(f"================Now Working on cirasame{cirasameID}================")
        working_excel_sheet = f"CIRASAME{cirasameID}"
        inputDAC_prev = excel_df_dict[working_excel_sheet]['Bias Indivisual'].to_list()
        cirasame_df, average_gain = dataframe_extract(df, cirasameID)
        gain_delta = []                                             # difference between gain and average

        # loop for citiroc
        for citiroc_num in range(1,5):
            citiroc_df = cirasame_df.loc[cirasame_df['citiroc']==citiroc_num]

            # loop for channel
            for ch in range(1, 33):
                row = citiroc_df.loc[citiroc_df['channel']==ch]
                delta = float(row['gain'] - average_gain)
                gain_delta.append(delta)

        inputDAC_shift = calculate_inputDAC_shift(gain_delta)
        shifted_inputDAC = [x+y for x,y in zip(inputDAC_prev, inputDAC_shift)]  # list of inputDAC after adjustment

        # re-writing new inputDAC value to dataframe
        shifted_inputDAC_series = pd.Series(shifted_inputDAC)
        excel_df_dict[working_excel_sheet]['Bias Indivisual'] = shifted_inputDAC_series
        
    print(excel_df_dict.items())
    
    # re-writing excel
    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
        for sheet, dataframe in excel_df_dict.items():
            dataframe.to_excel(writer, sheet_name=sheet, index=False)


if __name__=="__main__":
    main()