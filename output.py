import os
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import numpy as np
import csv 

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
    

    def output_as_csv(self, result_dataframe, vlimit1, vlimit2, filepath):
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
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)

                # Writing voltage limits
                writer.writerow(['Filename', filepath])
                writer.writerow(['Voltage Window (V)', vlimit1, vlimit2])
                #writer.writerow(['vlimit2', vlimit2])
                writer.writerow(['Notes', ])  # Add an empty row for separation

                # Writing the dataframe
                result_dataframe.to_csv(file, index=False)
            #messagebox.showinfo("Info", f'Data written to {filename}')

    def eis_to_csv(self, filepath, result_dataframe, notes):
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
            # Renaming columns
            result_dataframe = result_dataframe.rename(columns={'Zreal': 'Resistance (Ohms)'})
            result_dataframe = result_dataframe.rename(columns={'Freq': 'Frequency (Hz)'})

            # Export the dataframe to CSV
            with open(filename, mode='w', newline='') as file:
                writer = csv.writer(file)

                writer.writerow(['Filename', filepath])
                writer.writerow(['Notes', notes])
                writer.writerow([])
                result_dataframe.to_csv(file, index=False)

    def output_all_to_csv(self, result_dataframe, vlimit1, vlimit2, filepath):
            # Extract directory and original filename
            directory, original_filename = os.path.split(filepath)
            base_filename, _ = os.path.splitext(original_filename)
            output_filename = os.path.join(directory, f'{base_filename}_analysis.csv')

            # Export the dataframe to CSV
            with open(output_filename, 'w', newline='') as file:
                writer = csv.writer(file)
                
                # Writing voltage limits and filename
                writer.writerow(['Filename', original_filename])
                writer.writerow(['Voltage Window (V)', vlimit1, vlimit2])
                writer.writerow([])  # Add an empty row for separation

                # Writing the dataframe
                result_dataframe.to_csv(file, index=False, header=True)

            print(f'Data written to {output_filename}')
    
    def all_eis_to_csv(self, filepath, result_dataframe, notes):
            # Extract directory and original filename
            directory, original_filename = os.path.split(filepath)
            base_filename, _ = os.path.splitext(original_filename)
            output_filename = os.path.join(directory, f'{base_filename}_analysis.csv')
            # Renaming columns
            result_dataframe = result_dataframe.rename(columns={'Zreal': 'Resistance (Ohms)'})
            result_dataframe = result_dataframe.rename(columns={'Freq': 'Frequency (Hz)'})
            # Export the dataframe to CSV
            with open(output_filename, mode='w', newline='') as file:
                writer = csv.writer(file)

                writer.writerow(['Filename', filepath])
                writer.writerow(['Notes', notes])
                writer.writerow([])
                result_dataframe.to_csv(file, index=False, header=True)

            print(f'Data written to {output_filename}')

    


    




        
