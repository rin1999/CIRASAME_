#!/usr/bin/env python3

# This script is meant to automatise CIRASAME register settings.
# The register setting information of multiple (18) CIRASAMEs is found on a spreadsheet on Google Drive.
# At this moment you need to download the spread sheet in an xlsx format and pass it to this script. 
# Ideally the script access directly the file on the Google Drive, but in order to use API, it seems to 
# require a subscription with some payment method. Anyways.
# The script collect information from the xlsx file, modify relevant part of existing YAML files.
# Finally the C++ code is invoked that uses the YAML files. 3 seconds sleep is inserted after each 
# invokation of registry modification programme.
#
#
# created on 18.4.2024

import os
import subprocess
import argparse
import logging
import openpyxl
import yaml
import time
import pprint

def access_local_excel(file_path):

    cirasame_common = access_excel_cirasame_common(file_path)
    inputdac = access_excel_cirasame_individual(file_path, len(cirasame_common['ip_address'].keys()))
    
    return cirasame_common, inputdac

def access_excel_cirasame_individual(file_path, n_cirasame):
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    inputdac = []

    for i_cirasame in range(n_cirasame):

        sheet = workbook[f"CIRASAME{i_cirasame+1}"]       # HERE!!!!!!!!!!
        column_citiroc_number = find_column_number(sheet, "CITIROC#")
        column_channel_number = find_column_number(sheet, "Channel#")
        column_biasindividual_number = find_column_number(sheet, "Bias Individual")
        column_biasindividual_number = 3

        inputdac_list = [[0 for _ in range(32)] for _ in range(4)] # initialisation

        for row in sheet.iter_rows(min_row=2, values_only=True):
            citiroc_number = int(row[column_citiroc_number-1] - 1)
            channel_number = int(row[column_channel_number-1] - 1)
            bias_individual = row[column_biasindividual_number-1]
            inputdac_list[citiroc_number][channel_number] = bias_individual
      
        inputdac.append(inputdac_list)

    return inputdac

def access_excel_cirasame_common(file_path):
    """Access local Excel file and read IP addresses and values."""
    logging.info(f"Reading a local xlsx file: {file_path}")
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    sheet = workbook["CIRASAME Common"]

    column_cirasame_number = find_column_number(sheet, "CIRASAME#")
    column_ip_address = find_column_number(sheet, "IP Address")
    column_yaml_path = find_column_number(sheet, "YAML path")
    column_InputDAC_yml_filename = find_column_number(sheet, "InputDAC YAML file name")
    column_Register_yml_filename = find_column_number(sheet, "Register YAML file name")
    column_DiscriMask_yml_filename = find_column_number(sheet, "DiscriMask YAML file name")
    column_bias_common = find_column_number(sheet, "Bias Common")
    column_threshold_common_1 = find_column_number(sheet, "Threshold Common 1")
    column_threshold_common_2 = find_column_number(sheet, "Threshold Common 2")
    column_threshold_common_3 = find_column_number(sheet, "Threshold Common 3")
    column_threshold_common_4 = find_column_number(sheet, "Threshold Common 4")

    # Initialize dictionary to store IP addresses
    ip_addresses = {}
    yaml_pathes = {}
    bias = {}
    threshold = {}
    thresholds = {}
    InputDAC_yml_filenames = {}
    Register_yml_filenames = {}
    DiscriMask_yml_filenames = {}

    # Iterate over rows in the "CIRASAME common" tab
    for row in sheet.iter_rows(min_row=2, values_only=True):
        cirasame_number = row[column_cirasame_number-1]
        ip_address = row[column_ip_address-1]
        yaml_path = row[column_yaml_path-1]
        InputDAC_yml_filename = row[column_InputDAC_yml_filename-1]    
        Register_yml_filename = row[column_Register_yml_filename-1]
        DiscriMask_yml_filename = row[column_DiscriMask_yml_filename-1]
        bias = row[column_bias_common-1]
        threshold[1] = row[column_threshold_common_1-1]
        threshold[2] = row[column_threshold_common_2-1]
        threshold[3] = row[column_threshold_common_3-1]
        threshold[4] = row[column_threshold_common_4-1]
#        print(cirasame_number, yaml_path, ip_address, bias, threshold[1])

        ip_addresses[cirasame_number] = ip_address
        yaml_pathes[cirasame_number] = yaml_path
        InputDAC_yml_filenames[cirasame_number] = InputDAC_yml_filename
        Register_yml_filenames[cirasame_number] = Register_yml_filename
        DiscriMask_yml_filenames[cirasame_number] = DiscriMask_yml_filename

       # Store Threshold values in the Threshold dictionary
        if cirasame_number not in thresholds:
            thresholds[cirasame_number] = {}
        for citiroc_number in range(1, 5):  # Columns "Threshold Common 1" to "Threshold Common 4"
            thresholds[cirasame_number][citiroc_number] = threshold[citiroc_number]

    cirasame_common = {}
    cirasame_common['ip_address'] = ip_addresses
    cirasame_common['yaml_path'] = yaml_pathes
    cirasame_common['InputDAC_yml_filename'] = InputDAC_yml_filenames
    cirasame_common['Register_yml_filename'] = Register_yml_filenames
    cirasame_common['DiscriMask_yml_filename'] = DiscriMask_yml_filenames
    cirasame_common['threshold'] = thresholds
            
    logging.info(f"{len(ip_addresses)} CIRASAMEs are found.")
        
    return cirasame_common

def find_column_number(sheet, column_name):
    """Find the column number based on the column name."""
    for cell in sheet[1]:
        if cell.value == column_name:
            return cell.column

    # If column name is not found, return None
    logging.error(f"The column name {column_name} not found. Check the xlsx file.")
    return None

def modify_yaml_register(args, yaml_path, Register_yml_filename, thresholds):
    yaml_file = yaml_path + '/' + Register_yml_filename
    with open(str(yaml_file), 'r') as file:
        data = yaml.safe_load(file)

        logging.info(f"The file {yaml_file} will be modified.")
        for i in range(4):
            keyname = f"CITIROC{i+1}"
            logging.debug(f"   {keyname} DAC2 code: {data[keyname]['DAC2 code']} ==> {thresholds[i+1]}")
            data[keyname]['DAC2 code'] = int(thresholds[i+1])
            
    if args.execute:
        with open(str(yaml_file), 'w') as file:
            yaml.dump(data, file)

def modify_yaml_inputdac(args, yaml_path, InputDAC_yml_filename, inputdac):
    yaml_file = yaml_path + '/' + InputDAC_yml_filename
    with open(str(yaml_file), 'r') as file:
        data = yaml.safe_load(file)

        logging.info(f"The file {yaml_file} will be modified.")
        for icitiroc in range(4):
            for ichannel in range(32):
                keyname = f"CITIROC{icitiroc+1}"
                logging.debug(f"   {keyname} {ichannel+1}: {data[keyname]['Input 8-bit DAC'][ichannel]} ==> {inputdac[icitiroc][ichannel]}")
                data[keyname]['Input 8-bit DAC'][ichannel] = inputdac[icitiroc][ichannel]

    if args.execute:
        with open(str(yaml_file), 'w') as file:
            yaml.dump(data, file)

def main():
    parser = argparse.ArgumentParser(description="Process Excel file and invoke C++ binary script")
    parser.add_argument("file_path_or_id", help="Path to the local Excel file or ID of the Excel file on Google Drive")
    parser.add_argument("-m", "--mode", choices=["remote", "local"], default="local", help="Mode to run (remote or local)")
    parser.add_argument("-x", "--execute", action="store_true", help="Execute the script (default: dry run)")
    parser.add_argument("-l", "--loglevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO', help="Set the logging level")
    args = parser.parse_args()

    logging.basicConfig(level=logging.getLevelName(args.loglevel), format='%(message)s')

    if args.execute:
        print("Running in an execute mode.")
    else:
        print("Running in a dry-run mode. Use -x or --execute to actually modify yaml file and execute the femcitiroc_control.")

    if args.mode == "remote":
        print("the option not supported yet")
    elif args.mode == "local":
        cirasame_common, inputdac = access_local_excel(args.file_path_or_id)

    for cirasame_number in cirasame_common['ip_address'].keys():
        ip_address = cirasame_common['ip_address'][cirasame_number]
        threshold = cirasame_common['threshold'][cirasame_number]
        yaml_path = cirasame_common['yaml_path'][cirasame_number]
        InputDAC_yml_filename = cirasame_common['InputDAC_yml_filename'][cirasame_number]
        Register_yml_filename = cirasame_common['Register_yml_filename'][cirasame_number] 
        DiscriMask_yml_filename = cirasame_common['DiscriMask_yml_filename'][cirasame_number]

        # Modify yaml files to be read by the CIRASAME control programme.
        modify_yaml_register(args, yaml_path, Register_yml_filename, threshold)
        modify_yaml_inputdac(args, yaml_path, InputDAC_yml_filename, inputdac[int(cirasame_number)-1])
        
    if not args.execute:
        print('Do not forget to run in execute mode.')


if __name__ == "__main__":
    main()
