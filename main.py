import os
import tkinter as tk
from tkinter import filedialog
from data_loading import DataLoading
from preprocessing import Preprocessor

# Opens a file and asks whether it is one file or a folder
data_loader = DataLoading()
data_loader.open_file_dialog()
filepath = data_loader.get_file_path()
pathtype = data_loader.get_path_type()
print(f"Filepath: {filepath} Pathtype: {pathtype}")

"""ADD LOGIC FOR LOOPING DEPENDING ON PATHTYPE"""

# Determine CV or EIS
preprocessing = Preprocessor(filepath)
preprocessing.experiment_type()
experiment_type = preprocessing.get_experiment_type()
print(f"Experiment: {experiment_type}")

if 'CV' in experiment_type:
    preprocessing.pull_cv_metadata()
    curve_data = preprocessing.extract_cv_curves()
    print(curve_data)

elif experiment_type == 'EISPOT':
    pass



