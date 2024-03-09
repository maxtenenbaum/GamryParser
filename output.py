import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np

class Visualization:
    def __init__(self):
        self.output_path = None

    def open_save_dialog(self):
        root = tk.Tk()
        root.withdraw

        self.output_path = filedialog.asksaveasfilename(
            title = 'Select a save location',
            defaultextension = '.csv',
            filetypes=[("CSV files", "*.csv")]
            )

        if not self.output_path:
            raise ValueError("No path selected.")
    
    def get_save_path(self):
        return self.output_path
    

    def output_as_csv(self, result_dataframe):
            while True:
                root = tk.Tk()
                root.withdraw()

                filename = f'{self.output_path}'

                # Check if the file exists
                if os.path.exists(filename):
                    overwrite = messagebox.askyesno("Overwrite File", f"{filename} already exists. Overwrite?")
                    if not overwrite:
                        root.destroy()
                        self.open_save_dialog()  # Re-open save dialog to choose a new location
                        continue  # Restart the loop with the new path
                    else:
                        break  # Exit the loop if the user agrees to overwrite
                else:
                    break  # Exit the loop if the file doesn't exist

                root.destroy()

            # Export the dataframe to CSV
            result_dataframe.to_csv(filename, index=False)
            #messagebox.showinfo("Info", f'Data written to {filename}')




        
