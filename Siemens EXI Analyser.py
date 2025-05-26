import os
import pandas as pd
import warnings
import tkinter as tk
from tkinter import filedialog

# open folder and concatenate files
def get_raw_data(path):
    #fpath = paths + '/' + path + '/' + year
    files = os.listdir(path)     
    files_csv = [f for f in files if f[-3:] == 'csv']
    exi_log = pd.DataFrame()
    for f in files_csv:
        data = pd.read_csv(path + '/' + f, encoding_errors='ignore') #some Siemens systems produce an encoding error here so force ignore
        exi_log = pd.concat([exi_log,data])
    return exi_log

# renames columns - different Siemens models can have slightly different headers
# only renaming / checking those which are manipulated in this script
def rename_cols(exi_log):
    col_names = exi_log.columns.tolist()
    for header in col_names:
        if 'kV' in header:
            exi_log.rename(columns={header:'kV'}, inplace=True)
        elif 'mAs' in header:
            exi_log.rename(columns={header:'mAs'}, inplace=True)
        elif 'DAP' in header:
            exi_log.rename(columns={header:'DAP'}, inplace=True)
        elif 'Clin' in header:
            exi_log.rename(columns={header:'Clinical EXI'}, inplace=True)
        elif 'Collimation' in header:
            exi_log.rename(columns={header:'Collimation'}, inplace=True)
        elif 'SID' in header:
            exi_log.rename(columns={header:'SID'}, inplace=True)
        elif 'Dose' in header:
            exi_log.rename(columns={header:'Dose'}, inplace=True)

    return exi_log

	
# remove rows which contain a comma as a substring (i.e., remove bad data rows entirely)
# may be possible to keep these rows however they *should* account for a small number of total rows
# prints to console the exams which are removed - this may also remove some duplicated entries
def drop_commas(exi_log):
    length1 = exi_log.shape[0]
    for column in exi_log:
        exi_log = exi_log[~exi_log[column].astype(str).str.contains(',')]
    length2 = exi_log.shape[0]
    
    print("{} rows removed due to commas".format(length1-length2))
    return exi_log

# remove duplicate entries based on SOP Instance UID
def remove_duplicates(exi_log):
    exi_log = exi_log.drop_duplicates(subset=['SOP Instance UID'])
    return exi_log

def remove_prefixes(exi_log):
    # remove prefix on clinical EXI
    exi_log['Clinical EXI'] = exi_log['Clinical EXI'].str.removeprefix("(!) ")
    # remove prefix on OGP
    exi_log['OGP'] = exi_log['OGP'].str.removeprefix(" ")
    exi_log['OGP'] = exi_log['OGP'].str.removeprefix(",")
    exi_log['OGP'] = exi_log['OGP'].str.removeprefix("*")

    return exi_log

# split collimation into 2 columns
def split_collimation(exi_log):
    exi_log[['Collimation 1','Collimation 2']] = exi_log['Collimation'].str.split('x',expand=True)
    return exi_log

# change datatype of numeric columns reported on
def set_dtypes(exi_log):
    exi_log['DAP'] = pd.to_numeric(exi_log['DAP'])
    exi_log['Clinical EXI'] = pd.to_numeric(exi_log['Clinical EXI'])
    exi_log['Collimation 1'] = pd.to_numeric(exi_log['Collimation 1'])
    exi_log['Collimation 2'] = pd.to_numeric(exi_log['Collimation 2'])
    exi_log['SID'] = pd.to_numeric(exi_log['SID'])
    exi_log['Dose'] = pd.to_numeric(exi_log['Dose'], errors='coerce') #sets blanks to NaN
    
    #print(exi_log.info())
    
    return exi_log

# issue where sometimes DAP == 0. Removes entire row
def remove_zero_dap(exi_log):
    length3 = exi_log.shape[0]
    for column in exi_log:
        exi_log = exi_log[exi_log['DAP'] != 0]
    length4 = exi_log.shape[0]
    print("{} rows removed for zero DAP".format(length3-length4))

    return exi_log

def get_medians(exi_log):
    headers = {
        "Exam":[],
        "n":[],
        "kV":[],
        "mAs":[],
        "DAP":[],
        "EXI":[],
        "Collimation1":[],
        "Collimation2":[],
        "SID":[],
        "Dose":[]
    }
    median_df = pd.DataFrame(headers)
    unique_exams = exi_log['OGP'].unique()
    
    for exam in unique_exams:
    #    print(exi_log[exi_log["OGP"] == exam])
    #    try:
        exam_data = exi_log[exi_log["OGP"] == exam]
        n = exam_data.shape[0]
        kV = exam_data['kV'].median()
        mAs = exam_data['mAs'].median()
        DAP = exam_data['DAP'].median()
        EXI  = exam_data['Clinical EXI'].median()
        col1 = exam_data['Collimation 1'].median()
        col2 = exam_data['Collimation 2'].median()
        SID = exam_data['SID'].median()
        with warnings.catch_warnings(action='ignore'): #suppresses runtime warning as Dose is empty for many exams
            Dose = exam_data['Dose'].median()
        median_df.loc[len(median_df)] = [exam, n, kV, mAs, DAP, EXI, col1, col2, SID, Dose]

    return median_df

	
def save_df(df, path):
    df.to_csv(path)

	
root = tk.Tk()
root.withdraw()
input_dir = tk.filedialog.askdirectory(title="Select input folder")


try:
    exi_log = get_raw_data(input_dir)
except FileNotFoundError:
    print("Files could not be located\n")
        
exi_log = rename_cols(exi_log)
exi_log = drop_commas(exi_log)
exi_log = remove_duplicates(exi_log)
exi_log = remove_prefixes(exi_log)
exi_log = split_collimation(exi_log)
exi_log = set_dtypes(exi_log)
exi_log = remove_zero_dap(exi_log)
median_df = get_medians(exi_log)

output_dir = tk.filedialog.asksaveasfilename(title="Save As", defaultextension='.csv')
save_df(median_df, output_dir)

print("")

print("Complete")
