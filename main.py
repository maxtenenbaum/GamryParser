import os
import tkinter as tk
from tkinter import filedialog
from data_loading import DataLoading
from preprocessing import Preprocessor
from analysis import Analysis
from output import Visualization
import csv

# Opens a file and asks whether it is one file or a folder
data_loader = DataLoading()
data_loader.open_file_dialog()
filepath = data_loader.get_file_path()
pathtype = data_loader.get_path_type()
print(f"Filepath: {filepath} Pathtype: {pathtype}")


if pathtype == 'file':
    # Determine CV or EIS
    preprocessing = Preprocessor(filepath)
    preprocessing.experiment_type()
    experiment_type = preprocessing.get_experiment_type()
    #print(f"Experiment: {experiment_type}")

    if 'CV' in experiment_type:
        # Metadata
        preprocessing.pull_cv_metadata()
        # Extract Curves
        curve_data = preprocessing.extract_cv_curves()
        # Analysis
        surface_area = 0.0000199504 
        analysis = Analysis(curve_data, preprocessing.sampling_rate, surface_area)
        results = analysis.process_curves()
        # Output
        visualization = Visualization()
        visualization.open_save_dialog()
        save_path = visualization.get_save_path()
        name = filepath.split('/')[-1]
        visualization.output_as_csv(results, preprocessing.vlimit1, preprocessing.vlimit2, name)

    elif experiment_type == 'EISPOT':
        pass

if pathtype == 'folder':
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
                visualization = Visualization()
                saveway = f"{filepath}/{file}"
                visualization.output_all_to_csv(results, preprocessing.vlimit1, preprocessing.vlimit2, saveway)                        

