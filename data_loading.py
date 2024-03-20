import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

class DataLoading:
    def __init__(self):
        self.filepath = None
        self.pathtype = None
        self.file_or_directory = None
        self.additional_frequencies = []
        self.custom_freq = False

    def open_file_dialog(self):
        root = tk.Tk()
        root.withdraw()  # Hides the small tkinter window
        # Opens dialog for file selection
        self.filepath = filedialog.askopenfilename(
            title = "Select a file or containing folder",
            filetypes=[(".DTA Files", "*.DTA"),("All files", "*.*")])
            
        if not self.filepath:
            raise ValueError("No file was selected.")
        
        self.file_or_directory = messagebox.askquestion(title='File or folder', message='Analyze only this file? \n\nYes (single file) \nNo (all in folder)')
        if self.file_or_directory == 'no':
            self.filepath = self.filepath.rsplit('/',1)[0]
            self.pathtype = 'folder'
        if self.file_or_directory == 'yes':
            self.pathtype = 'file'
    
    def extra_eis_frequencies(self):
            ask_for_freq = messagebox.askquestion(title='Additional Frequencies', message='Would you like to set custom frequencies for output? \n\n (Default is 1Hz, 1kHz, 100kHz, 1MHz)')
            if ask_for_freq == 'no':
                self.custom_freq = False
            elif ask_for_freq == 'yes':
                self.custom_freq = True
                self.additional_frequencies = self.get_frequencies()
                #print("Selected frequencies:", self.additional_frequencies)

    def get_frequencies(self):
        input_str = simpledialog.askstring("Input Frequencies", "Enter frequencies in Hz separated by commas:")
        if input_str:
            try:
                frequencies = [float(freq.strip()) for freq in input_str.split(',')]
                return frequencies
            except ValueError:
                print("Invalid input. Please enter only numbers separated by commas.")
                return []
        else:
            return []
    
        


    def get_file_path(self):
        return self.filepath

    def get_path_type(self):
        return self.pathtype

