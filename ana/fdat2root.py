#!/usr/bin/env python3

import os
import sys
import argparse
from ROOT import TFile, TGraph, TCanvas, gROOT

def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert data files to TGraph and store in ROOT file.")
    parser.add_argument("-d", "--directory", type=str, help="Path to the directory containing data files.", required=True)
    parser.add_argument("-p", "--plot", action="store_true", help="Flag to show plot.")
    return parser.parse_args()

def create_tgraph(file_path):
    graph_list = []
    for y in range(1, 5):
        graph = TGraph()
        file_name = f"cirasame{file_path[-10:-7]}_{y}.dat"
        full_file_path = os.path.join(file_path, file_name)
        if os.path.exists(full_file_path):
            with open(full_file_path, 'r') as file:
                for line in file:
                    values = line.strip().split()
                    x, y_value = float(values[0]), float(values[1])
                    graph.SetPoint(graph.GetN(), x, y_value)
            graph_list.append(graph)
    return graph_list

def save_plots(graph_list, file_name):
    canvas = TCanvas("canvas", "Canvas", 800, 600)
    for i, graph in enumerate(graph_list):
        graph.Draw("APL")
        canvas.Update()
        canvas.Print(f"{file_name}_{i+1}.pdf")

def main():
    args = parse_arguments()
    directory_path = args.directory

    if not os.path.exists(directory_path):
        print("Error: Directory does not exist.")
        sys.exit(1)

    file_name = os.path.basename(os.path.normpath(directory_path))
    if directory_path == ".":
        file_name = input("Enter file name (default: fdat2root): ") or "fdat2root"

    root_file_name = f"{file_name}.root"
    pdf_file_name = f"{file_name}.pdf"

    root_file = TFile(root_file_name, "RECREATE")

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.startswith("cirasame") and file.endswith(".dat"):
                file_path = os.path.join(root, file)
                graph_list = create_tgraph(file_path)
                for i, graph in enumerate(graph_list):
                    graph_name = f"{file[:-4]}_{i+1}"
                    graph.SetName(graph_name)
                    graph.Write()

    root_file.Close()

    if args.plot:
        gROOT.SetBatch(False)
        graph_list = []
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.startswith("cirasame") and file.endswith(".dat"):
                    file_path = os.path.join(root, file)
                    graph_list.extend(create_tgraph(file_path))
        save_plots(graph_list, file_name)

if __name__ == "__main__":
    main()
