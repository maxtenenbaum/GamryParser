import os
import tkinter as tk
from tkinter import filedialog
from data_loading import DataLoading

# Opens a file and asks whether it is one file or a folder
data_loader = DataLoading()
data_loader.open_file_dialog()
filepath = data_loader.get_file_path()
pathtype = data_loader.get_path_type()

print(f"Filepath: {filepath} Pathtype: {pathtype}")


