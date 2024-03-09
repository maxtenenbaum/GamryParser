import os
import tkinter as tk
from tkinter import filedialog, messagebox

class DataLoading:
    def __init__(self):
        self.filepath = None
        self.pathtype = None
        self.file_or_directory = None

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

    def get_file_path(self):
        return self.filepath

    def get_path_type(self):
        return self.pathtype

