#!/usr/bin/env python3

import pandas as pd
import subprocess
import os
import argparse
import sys

HUL_PATH  = os.path.expanduser("~/cirasame/hul-common-lib/install/bin/set_max1932")
#XLSX_PATH = os.path.expanduser("~/cirasame/calib/xlsx")
SHEET_NAME= "CIRASAME Common"
IP_LIST = ['192.168.2.113','192.168.2.114','192.168.2.115',
           '192.168.2.116','192.168.2.117','192.168.2.118']

def inloop_process(sheet:pd.DataFrame, ip_address:str, isExecutable:bool, offset: int):
    bias_series = sheet.loc[sheet['IP Address']==ip_address, 'Bias Common']
    bias_list = bias_series.values
    bias_val = bias_list[0]
    input_bias = bias_val + offset
    if ((input_bias!=0)and(input_bias < 90)) or (input_bias >255):
        print("ERROR: BiasDAC out of range, or in dangerous area.")
        print("Stopping the process")
        sys.exit()
    if isExecutable:
        print(f"{HUL_PATH} {ip_address} {input_bias}  : executing...")
        subprocess.run([HUL_PATH, str(ip_address), str(int(input_bias))])
    else :
        print(f"{HUL_PATH} {ip_address} {input_bias}")
        

def read_xlsx(filepath:str, sheetname:str) -> pd.DataFrame:
    sheet = pd.read_excel(filepath, sheet_name=sheetname, engine="openpyxl")
    return sheet

def main(isExecutable:bool, xlsx_name: str, offset: int):
    sheet = read_xlsx(xlsx_name, SHEET_NAME)
    ip_addresses = sheet["IP Address"]
    for ip in IP_LIST:
        inloop_process(sheet, ip, isExecutable, offset)
    if not isExecutable:
        print('INFO: Do not forget to run in execute mode')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', required=True, help="excel file name")
    parser.add_argument('-o', '--offset', type=int, default=0, help="If you want to give some common offsets to bias, input an integer.")
    parser.add_argument('-x', action="store_true", help="Add this option when you execute")
    args = parser.parse_args()
    isExecutable = args.x
    xlsx_name = os.path.expanduser(args.name)
    offset = args.offset
    main(isExecutable, xlsx_name, offset)
