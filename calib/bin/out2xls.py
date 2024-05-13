#!/bin/env python3
# This script is in the part of the CIRASAME calibration script suit.
#
# The script reads the automatically determined threshold values by "pulseheightfit_all.C" script
# stored in ~/cirasame/calib/out/ and reflect them in an xls file.
#
# Input: ~/cirasame/calib/out/thresholdscan_YYYYMMDD_HHmm.out
# Output: ~/cirasame/calib/out/xls/cirasame_setting_hogehoge.xls
#
#
# created on 23.4.2024
import csv
import numpy as np
import os
import argparse
import logging
import openpyxl
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO)

import argparse
import openpyxl

def backup_excel_file(excel_file):
    dir_name = os.path.dirname(excel_file)
    base_name = os.path.basename(excel_file)

    backup_file = os.path.join(dir_name, f"{base_name}.backup")

    try:
        shutil.copy2(excel_file, backup_file)
        print(f"Backup created: {backup_file}")
    except Exception as e:
        print(f"Error creating backup: {e}")

def read_input_file(input_file):
    data = []
    with open(input_file, 'r') as f:
        for line in f:
            # Split the line by spaces
            row = line.strip().split()

            # Check if the row has 5 columns
            if len(row) != 5:
                print(f"Warning: Skipping line with invalid number of columns: {row}")
                continue

            # Replace "nan" or "-nan" with 0
            row = [0 if val.strip() in {"nan", "-nan"} else val for val in row]

            # Convert the values to float or int
            converted_row = []
            for val in row:
                try:
                    if "." in str(val):
                        converted_row.append(float(val))
                    else:
                        converted_row.append(int(val))
                except ValueError as e:
                    print(f"Warning: Skipping line with invalid value: {row}. Reason: {e}")
                    break
            else:
                data.append(converted_row)
    return data

def update_excel_file(excel_file, data):

    N_column_threshold = 3

    try:
        workbook = openpyxl.load_workbook(excel_file)
    except FileNotFoundError:
        print(f"Error: Excel file '{excel_file}' not found.")
        return
    try:
        sheet = workbook["CIRASAME Common"]
    except KeyError:
        print("Error: Worksheet 'CIRASAME Common' not found in the Excel file.")
        return

    # Get column numbers for specified column names
    column_names = ["Threshold Common 1", "Threshold Common 2", "Threshold Common 3", "Threshold Common 4"]
    column_numbers = {}
    for col in range(1, sheet.max_column + 1):
        column_name = sheet.cell(row=1, column=col).value
        for name in column_names:
            if name in column_name:
                number = int(column_name.split()[-1])
                column_numbers[number] = col
                # print(f"Column# for Threshold Common {number} is {col}")

    # Get row numbers for specified CIRASAME number
    cirasame_numbers = [i for i in range(1, 19)]
    row_numbers = {}
    for irow in range(2, sheet.max_row + 1):
        cirasame_number_in_sheet = int(sheet.cell(row=irow, column=1).value)
        for cirasame_number in cirasame_numbers:
            if (cirasame_number == cirasame_number_in_sheet):
                row_numbers[cirasame_number] = irow
                # print(f"Row# for CIRASAME {cirasame_number} is {irow} ")

    if len(column_numbers) != len(column_names):
        print("Error: Not all specified columns found in the worksheet.")
        return

    isSuspicious = 0
    for i, row_data in enumerate(data, start=1):
        global_asic_number = row_data[0]
        cirasame_number = global_asic_number // 4 + 1
        threshold_common_number = (i-1) % 4 + 1
        column_number_threshold_common = column_numbers[threshold_common_number]
        row_number_cirasame_number = row_numbers[cirasame_number]
        cell_value = sheet.cell(row=row_number_cirasame_number, column=column_numbers[threshold_common_number]).value
        #new_value = int(row_data[4])
        new_value = int(row_data[N_column_threshold])

        sheet.cell(row=row_number_cirasame_number, column=column_number_threshold_common, value=new_value)
        print(f"data line {i:3} (global asic# {global_asic_number:2}) {row_data[N_column_threshold]:10f} => sheet[{row_number_cirasame_number}][{column_number_threshold_common}]  {cell_value}")
        if (new_value == 0):
            isSuspicious+=1
    
    if (isSuspicious):
        print("Warning: Threshold value 0 found.")
    confirm = input("Do you want to apply the changes? [Y/n]: ").strip().lower()
    if confirm in {"y", "yes"}:
        backup_excel_file(excel_file)
        workbook.save(excel_file)
        print("Modification applied.")

def main():
    parser = argparse.ArgumentParser(description="Read the threshold value from the pulseheightfit_allb out file and save it to an Excel file.")
    parser.add_argument("input_file", help="Path to the input file")
    parser.add_argument("-o", "--output", default="~/cirasame/calib/xlsx/cirasame_setting.xlsx", help="Path to the output Excel file (default: output.xlsx)")
    args = parser.parse_args()

    data = read_input_file(args.input_file)
    update_excel_file(args.output, data)

if __name__ == "__main__":
    main()
