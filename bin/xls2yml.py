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

# Set up logging
logging.basicConfig(level=logging.INFO)

def access_local_excel(file_path):
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

    logging.info(f"{len(ip_addresses)} CIRASAMEs are found.")
        
    return ip_addresses, yaml_pathes, InputDAC_yml_filenames, Register_yml_filenames, DiscriMask_yml_filenames, bias, thresholds

def find_column_number(sheet, column_name):
    """Find the column number based on the column name."""
    for cell in sheet[1]:
        if cell.value == column_name:
            return cell.column

    # If column name is not found, return None
    return None

def modify_yaml(args, yaml_path, InputDAC_yml_filename, Register_yml_filename, DiscriMask_yml_filename, thresholds):
#    with open('RegisterValue.yml', 'r') as file:
    yaml_file = yaml_path + '/' + Register_yml_filename
    with open(str(yaml_file), 'r') as file:
        data = yaml.safe_load(file)

        # check
        # pprint.pprint(data)
        #print(data['CITIROC1']['DAC2 code'])

        # Writing back to YAML file
        logging.info(f"The file: {yaml_file} is modified. Thresholds are {thresholds}")
#        print(type(thresholds[1]))

        # Modifying data
        data['CITIROC1']['DAC2 code'] = int(thresholds[1])
        data['CITIROC2']['DAC2 code'] = int(thresholds[2])
        data['CITIROC3']['DAC2 code'] = int(thresholds[3])
        data['CITIROC4']['DAC2 code'] = int(thresholds[4])

    if args.execute:
        with open(str(yaml_file), 'w') as file:
            yaml.dump(data, file)


def set_thresholds(args, ip_address, yaml_path, InputDAC_yml_filename, Register_yml_filename, DiscriMask_yml_filename):
    """Invoke C++ binary script with IP address and thresholds."""
    InputDAC_yml_file_fullname = yaml_path + '/' + InputDAC_yml_filename
    Register_yml_file_fullname = yaml_path + '/' +  Register_yml_filename
    DiscriMask_yml_file_fullname = yaml_path + '/' + DiscriMask_yml_filename
    # logging.info(f"Invoking C++ binary script for IP address {ip_address} and value {thresholds}...")
    command = f"~/CIRASAME_Ctrl/CitirocControlSoft/bin/femcitiroc_control -ip={ip_address} -yaml={InputDAC_yml_file_fullname} -yaml={Register_yml_file_fullname} -yaml={DiscriMask_yml_file_fullname} -sc -read"

    logging.info(f"Invoking a command: {command}")
    if args.execute:
        os.system(str(command))
    else:
        print(command)

def main():
    parser = argparse.ArgumentParser(description="Process Excel file and invoke C++ binary script")
    parser.add_argument("file_path_or_id", help="Path to the local Excel file or ID of the Excel file on Google Drive")
    parser.add_argument("--mode", choices=["remote", "local"], default="local", help="Mode to run (remote or local)")
    parser.add_argument("-x", "--execute", action="store_true", help="Execute the script (default: dry run)")
    args = parser.parse_args()

    if args.execute:
        print("Running in an execute mode.")
    else:
        print("Running in a dry-run mode. Use -x or --execute to actually modify yaml file and execute the femcitiroc_control.")

    if args.mode == "remote":
        print("the option not supported yet")
        ip_addresses, yaml_pathes, InputDAC_yml_filenames, Register_yml_filenames, DiscriMask_yml_filenames, bias, thresholds = access_local_excel(args.file_path_or_id)
    elif args.mode == "local":
        ip_addresses, yaml_pathes, InputDAC_yml_filenames, Register_yml_filenames, DiscriMask_yml_filenames, bias, thresholds = access_local_excel(args.file_path_or_id)

    # Iterate through cirasame_number values
    for cirasame_number in ip_addresses.keys():
        ip_address = ip_addresses[cirasame_number]
        threshold = thresholds[cirasame_number]
        yaml_path = yaml_pathes[cirasame_number]
        InputDAC_yml_filename = InputDAC_yml_filenames[cirasame_number]
        Register_yml_filename = Register_yml_filenames[cirasame_number] 
        DiscriMask_yml_filename = DiscriMask_yml_filenames[cirasame_number]

        # Modify yaml files to be read by the CIRASAME control programme.
        modify_yaml(args, yaml_path, InputDAC_yml_filename, Register_yml_filename, DiscriMask_yml_filename, threshold)

        # Invoke C++ binary script to actually change the CIRASAME register.
#        set_thresholds(args, ip_address, yaml_path, InputDAC_yml_filename, Register_yml_filename, DiscriMask_yml_filename)
        time.sleep(1)

if __name__ == "__main__":
    main()
