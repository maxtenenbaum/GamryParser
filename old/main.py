import os
import tkinter as tk
from tkinter import filedialog
from data_loading import DataLoading
from preprocessing import Preprocessor
from analysis import Analysis
from analysis import EIS_Analysis
from output import Visualization
import csv
import pandas as pd

# Opens a file and asks whether it is one file or a folder
data_loader = DataLoading()
data_loader.open_file_dialog()
filepath = data_loader.get_file_path()
pathtype = data_loader.get_path_type()
#print(f"Filepath: {filepath} Pathtype: {pathtype}")


if pathtype == 'file':
    # Determine CV or EIS
    preprocessing = Preprocessor(filepath)
    preprocessing.experiment_type()
    experiment_type = preprocessing.get_experiment_type()
    visualization = Visualization()

    if 'CV' in experiment_type:
        preprocessing.pull_cv_metadata()
        curve_data = preprocessing.extract_cv_curves()
        surface_area = 0.0000199504 
        extras = preprocessing.get_extra_data()
        analysis = Analysis(curve_data, preprocessing.sampling_rate, surface_area)
        results = analysis.process_curves()
        visualization.open_save_dialog()
        save_path = visualization.get_save_path()
        name = filepath.split('/')[-1]
        visualization.output_as_csv(results, preprocessing.vlimit1, preprocessing.vlimit2, name)

    elif experiment_type.strip() == 'EISPOT':
        eis_analysis = EIS_Analysis()
        preprocessing.pull_eis_metadata()
        frequencies = data_loader.extra_eis_frequencies()
        dataframe = preprocessing.extract_eis(extra_data=False)
        dataframe = dataframe.drop(dataframe.index[0:2])
        frequencies = [1.0, 1000.0, 100000.0, 1000000.0]
        if data_loader.custom_freq:
            frequencies = frequencies + data_loader.additional_frequencies
        frequencies.sort()
        closest_frequencies = eis_analysis.get_closest_freq(dataframe, frequencies)
        filtered_df = dataframe[dataframe["Freq"].isin(closest_frequencies)]
        new_df = pd.DataFrame(' ', index=dataframe.index, columns=dataframe.columns)
        new_df.iloc[:len(filtered_df)] = filtered_df.values
        new_df['Zmod'] = dataframe['Zmod']
        new_df['Zphz'] = dataframe['Zphz']
        # Output to .csv
        visualization.open_save_dialog()
        save_path = visualization.get_save_path()
        name = filepath.split('/')[-1]
        visualization.eis_to_csv(name, new_df, preprocessing.notes)

if pathtype == 'folder':
    visualization = Visualization()
    for file in os.listdir(filepath):
        # Check the extension of each file
        base, ext = os.path.splitext(file)
        if ext.lower() == '.dta':  # Change '.dta' to your desired file extension
            full_path = os.path.join(filepath, file)
            preprocessing = Preprocessor(full_path)
            preprocessing.experiment_type()
            experiment_type = preprocessing.get_experiment_type()

            if 'CV' in experiment_type:
                # Metadata
                preprocessing.pull_cv_metadata()
                # Extract Curves
                curve_data = preprocessing.extract_cv_curves()
                # Analysis
                surface_area = 0.0000199504 
                analysis = Analysis(curve_data, preprocessing.sampling_rate, surface_area)
                results = analysis.process_curves()
                saveway = f"{filepath}/{file}"
                visualization.output_all_to_csv(results, preprocessing.vlimit1, preprocessing.vlimit2, saveway)                        

            elif experiment_type.strip() == 'EISPOT':
                eis_analysis = EIS_Analysis()
                preprocessing.pull_eis_metadata()
                frequencies = data_loader.extra_eis_frequencies()
                dataframe = preprocessing.extract_eis()
                dataframe = dataframe.drop(dataframe.index[0:2])
                frequencies = [1.0, 1000.0, 100000.0, 1000000.0]
                if data_loader.custom_freq:
                    frequencies = frequencies + data_loader.additional_frequencies
                frequencies.sort()
                closest_frequencies = eis_analysis.get_closest_freq(dataframe, frequencies)
                filtered_df = dataframe[dataframe["Freq"].isin(closest_frequencies)]
                new_df = pd.DataFrame(' ', index=dataframe.index, columns=dataframe.columns)
                new_df.iloc[:len(filtered_df)] = filtered_df.values
                new_df['Zmod'] = dataframe['Zmod']
                new_df['Zphz'] = dataframe['Zphz']                
                saveway = f"{filepath}/{file}"
                visualization.all_eis_to_csv(saveway, filtered_df, preprocessing.notes)