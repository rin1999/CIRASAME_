#!/usr/bin/env python3
#
#
#
#
import os
import argparse
import yaml
import sys
import time
import subprocess
import commonConfigReader
import logging
import datetime


DATA_BASEDIR    = "~/cirasame/calib/raw" # the threshold scan data base directory
CONFIG_BASEDIR  = "~/cirasame/calib/config" # the config yaml file base directory
CITIROC_PATH    = "~/cirasame/CitirocControlSoft/bin" # the CITIROC control software binary directory
HUL_PATH        = "~/cirasame/hul-common-lib/install/bin" # the HUL software binary directory
YAML_FILE       = "~/cirasame/calib/config/thresholdscan_range.yml" # the threshold scan range YAML file location
LOG_FILE        = "~/cirasame/calib/thresholdscan_log.txt" # the threshold log file

config_reader = commonConfigReader.CommonConfigReader()

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def open_thresholdscan_range_config_file():
    with open(os.path.expanduser(YAML_FILE), 'r') as file:
        data = yaml.safe_load(file)
    return data

def get_cirasame_ip_address(number):
    ip_address = config_reader.readCirasameIP(number)
#    return f"192.168.1.{number}"
    return ip_address

def get_loop_parameters(start, end, step):
    if (start is None) != (end is None) or (start is None) != (step is None):
        logging.error("Error: If any of start, end, or step is specified, all three parameters must be given.")
        exit(1)
    
    if start is not None and end is not None and step is not None:
        return int(start), int(end), int(step)
    else:
        # Read from YAML file
        configThresholdScanRange = config_reader.readThresholdScanRange()
#        config_yml = open_thresholdscan_range_config_file()
#        start = config_yml.get('start')
#        end = config_yml.get('end')
#        step = config_yml.get('step')
        start = configThresholdScanRange['start']
        end = configThresholdScanRange['end']
        step = configThresholdScanRange['step']
        
        if start is None or end is None or step is None:
            logging.error("Error: Missing loop parameters in YAML file.")
            exit(1)
        
        return int(start), int(end), int(step)

def get_config_path(cirasame_number):
    return f"{os.path.expanduser(CONFIG_BASEDIR)}/cirasame{cirasame_number:03d}"

def get_register_file_path(cirasame_number):
    config_path = get_config_path(cirasame_number)
    register_file_path = f"{config_path}/RegisterValue.yml"
    return register_file_path

def extract_info_from__register_config(cirasame_number):
    register_file_path = get_register_file_path(cirasame_number)
    PreAmp = [0, 0, 0, 0]
    with open(register_file_path, 'r') as f:
        yml_RegVal = yaml.safe_load(f)
        for iCITIROC in range (1, 5):
            icitiroc = f"CITIROC{iCITIROC}"
            PreAmp[iCITIROC-1] = yml_RegVal[icitiroc]['PreAMP']
    return PreAmp[0]

def save_original_register_config(cirasame_number):
    register_file_path = get_register_file_path(cirasame_number)
    with open(register_file_path, 'r') as f:
        return yaml.safe_load(f)

def restore_original_register_config(cirasame_number, original_register_config_file):
    register_file_path = get_register_file_path(cirasame_number)
    with open(register_file_path, 'w') as f:
        yaml.dump(original_register_config_file, f)

def set_register(cirasame_number, dac_threshold):
    register_path = get_register_file_path(cirasame_number)
    with open(register_path, 'r') as f:
        yml_RegVal = yaml.safe_load(f)
#        logging.info(f"start : DAC2 = {dac_threshold}")
        yml_RegVal['CITIROC1']['DAC2 code'] = dac_threshold
        yml_RegVal['CITIROC2']['DAC2 code'] = dac_threshold
        yml_RegVal['CITIROC3']['DAC2 code'] = dac_threshold
        yml_RegVal['CITIROC4']['DAC2 code'] = dac_threshold
#        logging.info(yml_RegVal['CITIROC1']['DAC2 code'])

    with open(register_path, 'w') as f:
        yaml.dump(yml_RegVal, f)
        
        """
        event, values = window.read(timeout=10)
        if event == 'Cancel' or event == sg.WIN_CLOSED:
        break
        window['-PROG-'].update(current_progress)
        current_progress = current_progress+1
        """
        
def measure(run_name, cirasame_number, threshold):
    #main part of reading scaler
    measurement_time = 1.0 # second
    register_path = get_register_file_path(cirasame_number)
    config_path = get_config_path(cirasame_number)
    citiroc_control_bin = f"{os.path.expanduser(CITIROC_PATH)}/femcitiroc_control"
    ip_address = get_cirasame_ip_address(cirasame_number)
    arg1 = f"-ip={ip_address}"
    arg2 = f"-yaml={config_path}/RegisterValue.yml"
    arg3 = f"-yaml={config_path}/InputDAC.yml"
    arg4 = f"-yaml={config_path}/DiscriMask.yml"
    hul_command_write = f"{os.path.expanduser(HUL_PATH)}/write_register"
    hul_command_read = f"{os.path.expanduser(HUL_PATH)}/read_scr"
    run_output_directory = get_run_output_directory(run_name)
    cirasame_output_directory = get_cirasame_output_directory(run_output_directory, cirasame_number)
    arg01 = f"{cirasame_output_directory}/binary/dataBin{threshold:03d}.dat"

    logging.info(f"{citiroc_control_bin} {arg1} {arg2} {arg3} {arg4} -sc -read -q")
    if logging.root.level <= logging.DEBUG:
        subprocess.run([citiroc_control_bin, arg1, arg2, arg3, arg4, '-sc', '-read', '-q'])
    else:
        out1 = subprocess.run([citiroc_control_bin, arg1, arg2, arg3, arg4, '-sc', '-read', '-q'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_str = out1.stdout.decode('utf-8')
        stderr_str = out1.stderr.decode('utf-8')
        grep_process = subprocess.Popen(["grep", "Timeout"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        timeoutmessage, _ = grep_process.communicate(out1.stdout)
        if timeoutmessage:
            logging.warning(f"{timeoutmessage}")
    logging.info(f"{hul_command_write} {ip_address} 0x80000000 0x1 1")

    out2 = subprocess.run([hul_command_write, ip_address, '0x80000000', '0x1', '1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # set the scaler value to zero
    time.sleep(measurement_time) 
    logging.info(f"{hul_command_read} {ip_address} {arg01}")
    out3 = subprocess.run([hul_command_read, ip_address, arg01], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def format_data(run_name, cirasame_number, start, end, step):

    run_directory = get_run_output_directory(run_name)  # e.g. ~/cirasame/calib/data/20240513_1200
    for threshold in range(start, end + 1, step):
        # Run the command and capture stdout as bytes
        cirasame_output_directory = get_cirasame_output_directory(run_directory, cirasame_number)
        argX = f"{cirasame_output_directory}/binary/dataBin{threshold:03d}.dat"
        output_file = f"{cirasame_output_directory}/decimal/dataDec{threshold:03d}.txt"
        output_bytes = subprocess.run(['od', '-Ad', '-td', '-v', argX], stdout=subprocess.PIPE).stdout

        # Decode stdout to a string
        output_str = output_bytes.decode('utf-8')  # Assuming UTF-8 encoding, adjust as needed
        #logging.info(output_str)
        with open(output_file, 'w') as f:
            f.write(output_str)
    
def scaler_measurement(run_name, cirasame_number, start, end, step):
    nstep = int((end-start+1)/step)
    istep = 0
    for threshold in range(start, end + 1, step):
        istep = istep + 1
        logging.warning(f"{istep:03d}/{nstep:03d}   CIRASAME{cirasame_number:02d} Threshold value: {threshold}")
        set_register(cirasame_number, threshold)
        measure(run_name, cirasame_number, threshold)
        #    logging.info(scan_dac_value)

def get_run_output_directory(run_name):
    # e.g. ~/cirasame/calib/data/20240513_1200
    return os.path.join(os.path.expanduser(DATA_BASEDIR), run_name)

def get_cirasame_output_directory(run_directory, cirasame_number):
    # e.g. ~/cirasame/calib/data/20240513_1200/cirasame001
    return os.path.join(run_directory, f"cirasame{cirasame_number:03d}")

def prepare_run_output_directory(run_name):
    run_directory = get_run_output_directory(run_name)
    if not os.path.exists(run_directory):
        os.makedirs(run_directory)
    return

def prepare_output_directory(run_name, cirasame_number):
    run_directory = get_run_output_directory(run_name)
    cirasame_directory = get_cirasame_output_directory(run_directory, cirasame_number)
    if os.path.exists(cirasame_directory):
        overwrite = input(f"Warning: directory {cirasame_directory} already exists. Do you want to overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            logging.warning("Exitting.")
            sys.exit(0)
    else:
        os.makedirs(cirasame_directory)
        create_directory(os.path.join(cirasame_directory, "binary"))
        create_directory(os.path.join(cirasame_directory, "decimal"))
    return

def write_meatadata_to_log(run_name, cirasame_number, start, end, step, extractedinfo):
    with open(os.path.expanduser(LOG_FILE), 'a') as file:
        current_datetime = datetime.datetime.now()
        logtext = f"{current_datetime}: {run_name} {cirasame_number} {start} {end} {step} {extractedinfo}"
        file.write(f"{logtext}\n")
    return

def main(run_name, cirasame_number, start=None, end=None, step=None):

    start, end, step = get_loop_parameters(start, end, step)
    prepare_run_output_directory(run_name)
    prepare_output_directory(run_name, cirasame_number)
    
    extractedinfo = extract_info_from__register_config(cirasame_number)
    write_meatadata_to_log(run_name, cirasame_number, start, end, step, extractedinfo)
    original_register_config_file = save_original_register_config(cirasame_number)
    scaler_measurement(run_name, cirasame_number, start, end, step) # loop
    restore_original_register_config(cirasame_number, original_register_config_file)
    format_data(run_name, cirasame_number, start, end, step) # loop
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Threshold Scan Script")
    parser.add_argument("-r", "--run", required=True, help="Run name")
    parser.add_argument("-n", "--number", type=int, required=True, help="CIRASAME number")
    parser.add_argument("-b", "--begin", type=int, help="Start value. e.g. 150")
    parser.add_argument("-e", "--end", type=int, help="End value. e.g. 600")
    parser.add_argument("-s", "--step", type=int, help="Step value. e.g. 1")
    parser.add_argument("-t", "--test", action='store_true', help="Enable test mode")
    parser.add_argument("-l", "--loglevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='WARNING', help="Set the logging level")
    args = parser.parse_args()

    logging.basicConfig(level=logging.getLevelName(args.loglevel), format='%(message)s')
    main(args.run, args.number, args.begin, args.end, args.step)
