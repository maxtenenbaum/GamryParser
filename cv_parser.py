"""
This program serves as a rudimentary command line interface for analyzing
cyclic voltammetry data

What has been done:
- We can parse metadata to understand the parameters of experiment
- We can obtain Qc/Qa/Qh and total charge from CV curves
- Use the last curve if not specified
- Add Qh (for sum of all not just positive or negative)
- Total anodic charge/total cathodic charge

What needs to be done:
- Output as .CSV with
- File name
- Total charge
- Add save location input
"""
import pandas as pd
import numpy as np
import os
import csv
import tkinter as tk
from tkinter import filedialog

#################
### FUNCTIONS ###
#################
#%%
"""def get_file_path():
    # Create a root window, but don't display it
    root = tk.Tk()
    root.withdraw()

    # Open the file dialog and store the selected file path
    file_path = filedialog.askopenfilename(
        defaultextension=".DTA",
        filetypes=[("DTA files", "*.DTA"), ("All files", "*.*")],
        title="Choose filepath to save CSV"
    )

    # Destroy the root window
    root.destroy()

    return file_path"""


def get_path():
    root = tk.Tk()
    root.withdraw()

    fileordir = input("Are you opening a file or folder? (file/folder): ").strip().lower()

    if fileordir == "file":
        path = filedialog.askopenfilename(
            defaultextension='.DTA',
            filetypes = [("DTA files", "*.DTA"),("All files", "*.*")],
            title = 'Choose a file'
        )
    elif fileordir == 'folder':
        path = filedialog.askdirectory(title="Choose a folder")
    else:
        print("Invalid input. Please enter 'file' or 'folder'")
        path = None

    root.destroy()
    return path


def parse_cv_metadata(filepath):
    """ 
    This function takes a .DTA file and returns:
    - Scan rate (mV/s)
    - Step size (mV)
    - Voltage limits (V)
    - Sampling rate (s)

    Example usage: scan_rate, step_size, vlimit1, vlimit2, sampling_rate = parse_cv_metadata(filepath)
    """
    scan_rate = float(0)
    step_size = float(0)
    vlimit1 = float(0)
    vlimit2 = float(0)
    total_time = float(0)
    with open(filepath, 'r') as file:
        lines = file.readlines()
    file_name = os.path.basename(filepath)
    date = lines[3].split('\t')[2]
    time = lines[4].split('\t')[2]
    device = 'N/A'
    electrolyte = 'N/A'
    for line in lines:
        split_line = line.split('\t')
        if split_line[0] == "SCANRATE":
            scan_rate = float(split_line[2])
        elif split_line[0] == "STEPSIZE":
            step_size = split_line[2]
        elif split_line[0] == "VLIMIT1":
            vlimit1 = float(split_line[2])
        elif split_line[0] == "VLIMIT2":
            vlimit2 = float(split_line[2])
    sampling_rate = float(step_size)/float(scan_rate)
    return scan_rate, step_size, vlimit1, vlimit2, sampling_rate



def extract_data(filepath):
    """ 
    This function takes an input file and extracts the CV curves

    It then creates a dictionary of all of the curves with the curve number
    as a key and a dataframe containing the voltage and current as the value

    Example usage: curve_dataframes = extract_data(filepath)
    """
    with open(filepath, 'r') as file:
        lines = file.readlines()

    curve_data = {}
    data_section = False
    headers = []
    current_curve = None

    for line in lines:
        if line.strip().startswith('CURVE') and line.strip().endswith('TABLE'):
            current_curve = line.strip().split('\t')[0]
            data_section = True
            curve_data[current_curve] = []
            continue

        if data_section:
            if line.startswith('\t#'):
                headers = line.strip().split('\t')[1:]
            elif line.startswith('\t'):
                values = line.strip().split('\t')[1:]
                if len(values) == len(headers):
                    curve_data[current_curve].append(values)

    for curve in curve_data:
        curve_df = pd.DataFrame(curve_data[curve], columns=headers)
        curve_df = curve_df.apply(pd.to_numeric, errors='ignore')
        curve_data[curve] = curve_df[['V vs. Ref.', 'A']]

    print(f"\nNumber of curves found: {len(curve_data)}")
    print("Curves:", list(curve_data.keys()))

    return curve_data



def spreadsheet(curve="CURVE4"):
    """
    This function takes a curve and returns:
    - Cathodal charge storage capacity (Qc)
    - Anodal charge storage capacity (Qa)
    - Total absolute charge/2 (Qh)
    - Total cathodal charge (EQc)
    - Total anodal chage (EQa)
    """

    # This finds the charge for each datapoint and adds a new column to the dataframe
    curve2 = curve_dataframes[curve][1::].copy()

    # Convert columns to numeric values
    curve2['A'] = pd.to_numeric(curve2['A'], errors='coerce')
    curve2['V vs. Ref.'] = pd.to_numeric(curve2['V vs. Ref.'], errors='coerce')
    # Initialize a new column 'Charges' with NaN (or zeros)
    curve2['Charge'] = 0.0

    # Calculate the rolling mean of 'A' for each pair of rows, then shift the result down by one row
    curve2['Charge'][1:] = (curve2['A'].rolling(window=2).mean()[1:]) * sampling_rate * 1000

    # Calculate the cumulative sum of 'Charge' and add it as 'Total Charge'
    curve2['Total Charge'] = curve2['Charge'].cumsum()

    # Calculate charge density and add a column
    curve2['Charge Density mC/cm2'] = curve2['Charge'] / surface_area

    # Calculate absolute charge
    curve2['Absolute Charge'] = abs(curve2['Charge'] / surface_area)


    # Cathodal integral value
    curve2['Cathodal Integral Value'] = np.where(curve2['Charge'] < 0, curve2['Charge Density mC/cm2'], 0)

    # Anodal integral value
    curve2['Anodal Integral Value'] = np.where(curve2['Charge'] >= 0, curve2['Charge Density mC/cm2'], 0)

    csc_c = abs(curve2['Cathodal Integral Value'].sum())
    csc_a = abs(curve2['Anodal Integral Value'].sum())
    total_cathodal_charge = csc_c*surface_area*1000000
    total_anodal_charge = csc_a*surface_area*1000000
    qh = abs(curve2['Absolute Charge'].sum())/2
    return csc_a, csc_c, total_anodal_charge, total_cathodal_charge, qh
    #print('Cathodal CSC:', csc_c)
    #print(total_cathodal_charge)
    #print('Anodal CSC:', csc_a)
    #print(total_anodal_charge)
    #print(curve2['A'],curve2['Charge'])


#%%
#################
#### PROGRAM ####
#################

# for test purposes
surface_area = 0.0000199504
# ASK FOR FILEPATH
selected_path = get_path()
if selected_path:
    if not selected_path.endswith('.DTA'):
        for file in os.listdir(selected_path):
            filepath = os.path.join(selected_path, file)

            print(f"\nFILEPATH: {filepath}")

            # Parse CV DATA
            scan_rate, step_size, vlimit1, vlimit2, sampling_rate = parse_cv_metadata(filepath)

            # Extract the data and present the data we have
            curve_dataframes = extract_data(filepath)

            # Curve selection
            print("\nWhich curve would you like to use: ")
            num = 1
            for i in curve_dataframes:
                print("Curve",num)
                num += 1
            while True:
                try:
                    curve_selection = input("\nSelect a curve: ")
                    curve_selection = int(curve_selection)

                    if curve_selection not in range(1, len(curve_dataframes)+1):
                        print("Invalid selection. Please enter a valid number.")
                    else:
                        curve = f"CURVE{curve_selection}"
                        break
                except ValueError:
                    print("Invalid input. Please enter a number.")

            # Process curve
            csc_a, csc_c, total_anodal_charge, total_cathodal_charge, qh = spreadsheet(curve)

            # Storage for .CSV export
            data = [
                ["Voltage window", f"{vlimit1}V", f"{vlimit2}V"],
                ["Qa", f"{round(csc_a, 3)} mC/cm2"],
                ["Total Anodal Charge", f"{round(total_anodal_charge, 3)}"],
                ["Qc", f"{round(csc_c, 3)} mC/cm2"],
                ["Total Cathodal Charge", f"{round(total_cathodal_charge, 3)}"],
                ["Qh", f"{round(qh, 3)} mC/cm2"]
            ]

            # Processed data
            print("\n\n\n#########################################")
            print("###############   OUTPUT   ##############")
            print("#########################################")

            print(f"\nVoltage window: {vlimit1}V :: {vlimit2}V")
            print(f"\nQa = {round(csc_a, 3)} mC/cm2")
            print(f"Total Anodal Charge = {round(total_anodal_charge,3)}")
            print(f"\nQc = {round(csc_c, 3)} mC/cm2")
            print(f"Total Cathodal Charge = {round(total_cathodal_charge,3)}")
            print(f"\nQh = {round(qh, 3)} mC/cm2")


            # Writing to CSV
            filename = f"{filepath[0:-4]}_{curve}_summary.csv"
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Writing each row
                for row in data:
                    writer.writerow(row)

            print(f"Data written to {filename}")

    else:
        print(f"\nFILEPATH: {selected_path}")

        # Parse CV DATA
        scan_rate, step_size, vlimit1, vlimit2, sampling_rate = parse_cv_metadata(selected_path)

        # Extract the data and present the data we have
        curve_dataframes = extract_data(selected_path)

        # Curve selection
        print("\nWhich curve would you like to use: ")
        num = 1
        for i in curve_dataframes:
            print("Curve",num)
            num += 1
        while True:
            try:
                curve_selection = input("\nSelect a curve: ")
                curve_selection = int(curve_selection)

                if curve_selection not in range(1, len(curve_dataframes)+1):
                    print("Invalid selection. Please enter a valid number.")
                else:
                    curve = f"CURVE{curve_selection}"
                    break
            except ValueError:
                print("Invalid input. Please enter a number.")

        # Process curve
        csc_a, csc_c, total_anodal_charge, total_cathodal_charge, qh = spreadsheet(curve)

        # Storage for .CSV export
        data = [
            ["Voltage window", f"{vlimit1}V", f"{vlimit2}V"],
            ["Qa", f"{round(csc_a, 3)} mC/cm2"],
            ["Total Anodal Charge", f"{round(total_anodal_charge, 3)}"],
            ["Qc", f"{round(csc_c, 3)} mC/cm2"],
            ["Total Cathodal Charge", f"{round(total_cathodal_charge, 3)}"],
            ["Qh", f"{round(qh, 3)} mC/cm2"]
        ]

        # Processed data
        print("\n\n\n#########################################")
        print("###############   OUTPUT   ##############")
        print("#########################################")

        print(f"\nVoltage window: {vlimit1}V :: {vlimit2}V")
        print(f"\nQa = {round(csc_a, 3)} mC/cm2")
        print(f"Total Anodal Charge = {round(total_anodal_charge,3)}")
        print(f"\nQc = {round(csc_c, 3)} mC/cm2")
        print(f"Total Cathodal Charge = {round(total_cathodal_charge,3)}")
        print(f"\nQh = {round(qh, 3)} mC/cm2")


        # Writing to CSV
        filename = f"{selected_path[0:-4]}_{curve}_summary.csv"
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Writing each row
            for row in data:
                writer.writerow(row)

        print(f"Data written to {filename}")
