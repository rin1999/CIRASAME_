#!/usr/bin/env python3
import numpy as np
import pandas as pd
import os
import xlsxSettingManager
import outFileReader
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

BEFORE_XLSX_PATH = os.path.expanduser("~/cirasame/calib/xlsx/crsm_setting_20240520_1030_lap3.xlsx")
BEFORE_OUT_PATH = os.path.expanduser("~/cirasame/calib/ana/out/threscan_ana_chan_20240520_1240.out")
AFTER_XLSX_PATH = os.path.expanduser("~/cirasame/calib/xlsx/crsm_setting_20240520_1030_lap4.xlsx")
AFTER_OUT_PATH = os.path.expanduser("~/cirasame/calib/ana/out/threscan_ana_chan_20240520_1420.out")
PDF_SAVE_PATH = os.path.expanduser("~/cirasame/calib/ana/pic/grad_20240520_1030_lap3to4.pdf")
START_CIRASAMEID = 1
END_CIRASAMEID = 18

def get_inputDAC_diff(xlsx_before, xlsx_after, i_cirasame) -> list:
    cirasame_sheet_before = xlsx_before.get_cirasame_sheet(i_cirasame)
    cirasame_sheet_after  = xlsx_after.get_cirasame_sheet(i_cirasame)
    inputDAC_before = cirasame_sheet_before['Bias Individual']
    inputDAC_after  = cirasame_sheet_after['Bias Individual']
    inputDAC_diff   = inputDAC_after - inputDAC_before
    return inputDAC_diff.tolist(), inputDAC_before.tolist(), inputDAC_after.tolist()


def get_gain_diff(out_before: outFileReader.OutFileReader, out_after: outFileReader.OutFileReader):
    df_out_before = out_before.get_outfile_ch()
    df_out_after = out_after.get_outfile_ch()
    gain_before = df_out_before['Gain DAC']
    gain_after  = df_out_after['Gain DAC']
    gain_diff   = gain_after-gain_before
    return gain_diff.tolist(), gain_before.tolist(), gain_after.tolist()
 

def main():
    xlsx_before = xlsxSettingManager.XlsxSettingManager(BEFORE_XLSX_PATH)
    xlsx_after = xlsxSettingManager.XlsxSettingManager(AFTER_XLSX_PATH)    
    out_before = outFileReader.OutFileReader(BEFORE_OUT_PATH)
    out_after = outFileReader.OutFileReader(AFTER_OUT_PATH)

    inputDAC_diff_matrix = [] # (after - before) [cirasameID][channel]
    inputDAC_before_2dlist = []
    inputDAC_after_2dlist = []

    for i_cirasame in range(START_CIRASAMEID, END_CIRASAMEID+1):
        inputDAC_diff_cirasame, inputDAC_before_list, inputDAC_after_list = get_inputDAC_diff(xlsx_before, xlsx_after, i_cirasame)
        inputDAC_diff_matrix.append(inputDAC_diff_cirasame)
        inputDAC_before_2dlist.append(inputDAC_before_list)
        inputDAC_after_2dlist.append(inputDAC_after_list)
    
    inputDAC_diff = [element for sublist in inputDAC_diff_matrix for element in sublist] # convert to 1d list
    inputDAC_before = [element for sublist in inputDAC_before_2dlist for element in sublist]
    inputDAC_after  = [element for sublist in inputDAC_after_2dlist for element in sublist]

    gain_diff, gain_before, gain_after = get_gain_diff(out_before, out_after)


    gradient = [gain/inputDAC if inputDAC!=0 else np.nan for gain, inputDAC in zip(gain_diff, inputDAC_diff)]
    gradient_withoutNaN = [x for x in gradient if not np.isnan(x)]
    """
    plot_index = []
    for i in range(len(gradient)):
        l =[]
        if gradient[i] != np.nan:
            #if (gradient[i]<-0.5 and gradient[i]>-1.1) or (gradient[i]<1.0 and gradient[i]>0.5):
                l.append(i)
        plot_index.append(l)
    """
    i_plot_list = []
    for i_cirasame in range(START_CIRASAMEID, END_CIRASAMEID+1):
        plot_index = []
        for i_ch in range(1, 129):
            i = i_cirasame*i_ch -1
            if gradient[i-1] == np.nan:
                continue
            else:
                plot_index.append(i-1)
        i_plot_list.append(plot_index)
    
    with PdfPages(PDF_SAVE_PATH) as pdf:
        for i_cirasame in range(START_CIRASAMEID, END_CIRASAMEID+1):
            print(f"plotting CIRASAME{i_cirasame}")
            plt.title(f"CIRASAME{i_cirasame}")
            plt.xlabel("inputDAC")
            plt.ylabel("Gain")
            plt.ylim(80,100)
            plt.xlim(77, 177)
            #plt.axvline(x=1/3.8, color='red', linestyle='-')
            gain_list = []
            for i_ch in range(1, 129):
                i = i_cirasame*i_ch -1
                if gradient[i-1] == np.nan:
                    continue
                else:
                    x = [inputDAC_before[i], inputDAC_after[i]]
                    y = [gain_before[i], gain_after[i]]
                    gain_list.append(gain_before[i])
                    plt.grid(True)
                    plt.text(3, 8, 'This is a text block', fontsize=12, color='red', ha='center', va='center', bbox=dict(facecolor='lightgray', edgecolor='black', boxstyle='round,pad=1'))
                    if inputDAC_after[i]-inputDAC_before[i] > 0:
                        plt.scatter(x[0], y[0], color='red', s=5)
                        plt.scatter(x[1], y[1], color='red', s=5)
                        plt.annotate('', xy=(x[1], y[1]), xytext=(x[0], y[0]), arrowprops=dict(arrowstyle='->', color='red'))
                        #plt.plot(x,y, label=f"i={i}", linestyle='-', linewidth=0.3, marker='o', markersize=2, color='red')   
                    else:
                        plt.scatter(x[0], y[0], color='blue', s=5)
                        plt.scatter(x[1], y[1], color='blue', s=5)
                        plt.annotate('', xy=(x[1], y[1]), xytext=(x[0], y[0]), arrowprops=dict(arrowstyle='->', color='blue'))
                        #plt.plot(x,y, label=f"i={i}", linestyle='-', linewidth=0.3, marker='o', markersize=2, color='blue')
            gain_mean = np.mean(gain_list)
            print(f"gain ave(cirasame{i_cirasame}) = {gain_mean}")
            plt.axhline(y=gain_mean, color='red', linestyle='--')
            pdf.savefig()
            plt.close()

        plt.grid(True)
        plt.hist(gradient_withoutNaN, bins=30, range=(-1.5,1.5))
        plt.xlabel("gradient_gain/inputDAC")
        plt.axvline(x=1/3.8, color='red', linestyle='-')
        plt.xlabel("inputDAC")
        plt.ylabel("Counts")
        pdf.savefig()

    #plt.savefig(PDF_SAVE_PATH, format='pdf')


if __name__=="__main__":
    main()