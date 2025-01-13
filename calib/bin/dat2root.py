#!/usr/bin/env python3
'''
Description comes here

created 23.05.2024
'''
import argparse
import os
import subprocess
import warnings


fdat_dir = "~/cirasame/calib/data_formated"
ana_dir = "~/cirasame/calib/ana"
root_dir = "~/cirasame/calib/ana/root"
bin_dat2fdat_dir = "~/cirasame/calib/bin"
root_macro_filename_dat2root = "dat2root.C"
root_macro_filename_threscan = "threscan_ana_current.C"

def convert_dat_to_fdat(run_name, dry_run):
    bin_dat2fdat_dir2 = os.path.expanduser(bin_dat2fdat_dir)
    cmd_dat2fdat = f"{bin_dat2fdat_dir2}/dat2fdat.py"
    arg1 = f"-n {run_name}"
    print(f"Converting dat to fdat:")
    print(f"    {cmd_dat2fdat} {arg1}")
    if not dry_run:
        subprocess.run([cmd_dat2fdat, arg1])
    return

def convert_fdat_to_root(run_name, dry_run):
    ana_dir2 = os.path.expanduser(ana_dir)
    fdat_dir2 = os.path.expanduser(fdat_dir)
    cmd_macro_fdat2root = f".x {ana_dir2}/fdat2root.C(\"{fdat_dir2}/thresholdscan_{run_name}\")"
    root_macro_path = f"{ana_dir2}/{root_macro_filename_dat2root}"
    cmd_root = f"root"
    arg1_cmd_root = "-b"
    arg2_cmd_root = "-q"
    arg3_cmd_root = f"{root_macro_path}"
    print(f"Converting fdat to root:")
    print(f"    {cmd_root} {arg1_cmd_root} {arg2_cmd_root} {arg3_cmd_root}")
    print(f"    {cmd_macro_fdat2root}")
    if not dry_run:
        with open(root_macro_path, 'w') as f:
            f.write(f"{cmd_macro_fdat2root};\n")
            subprocess.run([cmd_root, arg1_cmd_root, arg2_cmd_root, arg3_cmd_root])
    return

def analyse_thresholdscan(run_name, dry_run):
    ana_dir2 = os.path.expanduser(ana_dir)
    root_dir2 = os.path.expanduser(root_dir)
    macro_name = "threscan_ana_newfit.C"
    cmd_macro_threscan = f".x {ana_dir2}/{macro_name}(\"{root_dir2}/thresholdscan_{run_name}.root\")"
    root_macro_path = f"{ana_dir2}/{root_macro_filename_threscan}"
    cmd_root = "root"
    arg1_cmd_root = "-b"
    arg2_cmd_root = "-q"
    arg3_cmd_root = f"{root_macro_path}"
    print(f"Analysing data:")
    print(f"    {cmd_root} {arg1_cmd_root} {arg2_cmd_root} {arg3_cmd_root}")
    print(f"    {cmd_macro_threscan}")
    if not dry_run:
        with open(root_macro_path, 'w') as f:
            f.write(f"{cmd_macro_threscan};\n")
        subprocess.run([cmd_root, arg1_cmd_root, arg2_cmd_root, arg3_cmd_root])
    return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--run_name", required=True, type=str, help='scan run name e.g. 20240422_2200')
    parser.add_argument("-d", "--dry_run", action="store_true", help='dry run')
    args = parser.parse_args()

    convert_dat_to_fdat(args.run_name, args.dry_run)
    convert_fdat_to_root(args.run_name, args.dry_run)
    analyse_thresholdscan(args.run_name, args.dry_run)

if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=FutureWarning)
    main()
