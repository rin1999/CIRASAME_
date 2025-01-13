#!/usr/bin/env python3
import numpy as np
import pandas as pd

class XlsxSettingManager:
    def __init__(self, xlsxpath) -> None:
        self.data = pd.read_excel(xlsxpath, sheet_name=None, engine="openpyxl")

    def get_common_sheet(self) -> pd.DataFrame:
        sheet = self.data["CIRASAME Common"]
        return sheet
    
    def get_cirasame_sheet(self, cirasameID: int) -> pd.DataFrame:
        sheet = self.data[f"CIRASAME{cirasameID}"]
        return sheet
