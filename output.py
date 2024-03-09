import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np

class Visualization:
    def __init__(self):
        self.output_path = None

    def open_save_dialog(self):
        root = tk.Tk()
        root.withdraw

        self.output_path = filedialog.asksaveasfilename(title = 'Select a save location')

        if not self.output_path:
            raise ValueError("No path selected.")
    
    def get_save_path(self):
        return self.output_path
    

    def output_as_csv(self, result_dataframe):
        filename = f'{self.output_path}.csv'
        result_dataframe.to_csv(filename, index=False)
        print(f'Data written to {filename}')


        
