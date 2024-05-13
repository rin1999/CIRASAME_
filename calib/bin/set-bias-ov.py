#!/usr/bin/env python3

import os
import subprocess
import argparse
import logging
import openpyxl
import yaml
import pprint

# Set up logging
logging.basicConfig(level=logging.INFO)

def access_local_excel(file_path):
    """Access local Excel file and read IP addresses and values."""
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active
    sheet = workbook["CIRASAME Common"]

    column_cirasame_number = find_column_number(sheet, "CIRASAME#")
    column_ip_address = find_column_number(sheet, "IP Address")
    column_yaml_path = find_column_number(sheet, "YAML path")
    column_bias_common_1 = find_column_number(sheet, "Bias Common 1")
    column_bias_common_2 = find_column_number(sheet, "Bias Common 2")
    column_bias_common_3 = find_column_number(sheet, "Bias Common 3")
    column_bias_common_4 = find_column_number(sheet, "Bias Common 4")
    column_threshold_common_1 = find_column_number(sheet, "Threshold Common 1")
    column_threshold_common_2 = find_column_number(sheet, "Threshold Common 2")
    column_threshold_common_3 = find_column_number(sheet, "Threshold Common 3")
    column_threshold_common_4 = find_column_number(sheet, "Threshold Common 4")

    # Initialize dictionary to store IP addresses
    ip_addresses = {}
    yaml_pathes = {}
    bias = {}
    threshold = {}
    biases = {}
    thresholds = {}

    # Iterate over rows in the "CIRASAME common" tab
    for row in sheet.iter_rows(min_row=2, values_only=True):
        cirasame_number = row[column_cirasame_number-1]
        ip_address = row[column_ip_address-1]
        yaml_path = row[column_yaml_path-1]
        bias[1] = row[column_bias_common_1-1]
        bias[2] = row[column_bias_common_2-1]
        bias[3] = row[column_bias_common_3-1]
        bias[4] = row[column_bias_common_4-1]
        threshold[1] = row[column_threshold_common_1-1]
        threshold[2] = row[column_threshold_common_2-1]
        threshold[3] = row[column_threshold_common_3-1]
        threshold[4] = row[column_threshold_common_4-1]
        print(cirasame_number, yaml_path, ip_address, bias[1], threshold[1])

        ip_addresses[cirasame_number] = ip_address
        yaml_pathes[cirasame_number] = yaml_path

        # Initialize biases dictionary for the current CIRASAME# if not already done
        if cirasame_number not in biases:
            biases[cirasame_number] = {}
        for citiroc_number in range(1, 5):  # Columns "Bias Common 1" to "Bias Common 4"
            biases[cirasame_number][citiroc_number] = bias[citiroc_number]

       # Store Threshold values in the Threshold dictionary
        if cirasame_number not in thresholds:
            thresholds[cirasame_number] = {}
        for citiroc_number in range(1, 5):  # Columns "Threshold Common 1" to "Threshold Common 4"
            thresholds[cirasame_number][citiroc_number] = threshold[citiroc_number]
        
    return ip_addresses, yaml_pathes, biases, thresholds

def find_column_number(sheet, column_name):
    """Find the column number based on the column name."""
    for cell in sheet[1]:
        if cell.value == column_name:
            return cell.column

    # If column name is not found, return None
    return None

def modify_yaml(yaml_path, biases, thresholds):
#    with open('RegisterValue.yml', 'r') as file:
    with open(str(yaml_path), 'r') as file:
        data = yaml.safe_load(file)

        # check
        #pprint.pprint(data)
        #print(data['CITIROC1']['DAC2 code'])

        # Modifying data
        data['CITIROC1']['DAC2 code'] = threholds[1]
        data['CITIROC2']['DAC2 code'] = threholds[2]
        data['CITIROC3']['DAC2 code'] = threholds[3]
        data['CITIROC4']['DAC2 code'] = threholds[4]

        # Writing back to YAML file
#        yaml.dump(data, file)


def convert_value(value):
    """Convert value using a custom conversion function."""
    # Define the conversion logic here
    # Placeholder implementation
    return value * 2

def set_biases(ip_address, bias):
    """Invoke C++ binary script with IP address and converted value."""
    # Invoke C++ binary script with IP address and converted value as arguments
    logging.info(f"Invoking C++ binary script for IP address {ip_address} and value {bias}...")
#    subprocess.run(["./your_cpp_binary", ip_address, str(bias[0])], check=True)

def main():
    parser = argparse.ArgumentParser(description="Process Excel file and invoke C++ binary script")
    parser.add_argument("file_path_or_id", help="Path to the local Excel file or ID of the Excel file on Google Drive")
    parser.add_argument("--mode", choices=["remote", "local"], default="local", help="Mode to run (remote or local)")
    args = parser.parse_args()

    if args.mode == "remote":
        print("the option not supported yet")
        ip_addresses, yaml_pathes, biases, thresholds = access_local_excel(args.file_path_or_id)
    elif args.mode == "local":
        ip_addresses, yaml_pathes, biases, thresholds = access_local_excel(args.file_path_or_id)

    # Iterate through cirasame_number values
    for cirasame_number in ip_addresses.keys():
        ip_address = ip_addresses[cirasame_number]
        bias = biases[cirasame_number]
        threshold = thresholds[cirasame_number]
        yaml_path = yaml_pathes[cirasame_number]

        modify_yaml(yaml_path, bias, threshold)

        # Print or use the values as needed
#        print(f"IP Address for CIRASAME#{cirasame_number}: {ip_address}")
#        print(f"Biases for CIRASAME#{cirasame_number}: {bias}")
#        print(f"Thresholds for CIRASAME#{cirasame_number}: {threshold}")

        # Invoke C++ binary script
        set_biases(ip_address, bias)

if __name__ == "__main__":
    main()
