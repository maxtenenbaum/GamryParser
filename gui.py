import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import csv
from ttkthemes import ThemedTk
from data_loading import DataLoading
from preprocessing import Preprocessor
from analysis import Analysis
from analysis import EIS_Analysis
from output import Visualization

class App(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.root = master
        self.root.title("GamryParser")
        self.listbox = None
        self.listbox_shown = False
        self.data_loader = DataLoading()
        self.visualization = Visualization()
        
        self.choices = ["Option 1", "Option 2", "Option 3", "Option 4"]
        
        # Set light mode theme
        self.set_light_theme()

        # Configure root window
        self.root.geometry("800x600")
        
        # Create the main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Set weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Create a frame for the buttons and settings
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.N, tk.W), padx=10, pady=10)

        # Create a frame for the Load File button
        self.load_frame = ttk.Frame(self.button_frame)
        self.load_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Create the Load File button
        self.file_button = ttk.Button(self.load_frame, text="Load File", command=self.load_file)
        self.file_button.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Create a frame for CV settings
        self.cv_frame = ttk.Labelframe(self.button_frame, text="CV Settings")
        self.cv_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Create settings for CV
        self.checkbox_var = tk.BooleanVar()
        self.checkbox = ttk.Checkbutton(self.cv_frame, text="Custom Select Curves", variable=self.checkbox_var, command=self.toggle_listbox)
        self.checkbox.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.cv_setting2_label = ttk.Label(self.cv_frame, text="CV Setting 2:")
        self.cv_setting2_label.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W))
        
        self.cv_setting2_entry = ttk.Entry(self.cv_frame)
        self.cv_setting2_entry.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Create a frame for EIS settings
        self.eis_frame = ttk.Labelframe(self.button_frame, text="EIS Settings")
        self.eis_frame.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Create settings for EIS
        self.eis_setting1_label = ttk.Label(self.eis_frame, text="EIS Setting 1:")
        self.eis_setting1_label.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W))
        
        self.eis_setting1_entry = ttk.Entry(self.eis_frame)
        self.eis_setting1_entry.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        self.eis_setting2_label = ttk.Label(self.eis_frame, text="EIS Setting 2:")
        self.eis_setting2_label.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W))
        
        self.eis_setting2_entry = ttk.Entry(self.eis_frame)
        self.eis_setting2_entry.grid(row=3, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # Create the Parse button
        self.parse_button = ttk.Button(self.button_frame, text="Parse", command=self.parse)
        self.parse_button.grid(row=3, column=0, padx=5, pady=20, sticky=(tk.W, tk.E))
        
        # Create a Treeview to display CSV content
        self.tree = ttk.Treeview(self.main_frame, columns=(), show="headings")
        self.tree.grid(row=0, column=1, rowspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Create a status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.update_status("Ready")










    def set_light_theme(self):
        # Apply a ttkthemes theme
        self.root.set_theme("arc")  # Choose a modern, light theme like 'arc', 'adapta', 'plastik', etc.

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def load_file(self):
        self.update_status("Loading file...")
        self.data_loader.open_file_dialog()
        filepath = self.data_loader.get_file_path()
        self.process_file(filepath)
        
    def process_file(self, filepath):
        pathtype = self.data_loader.get_path_type()
        
        if pathtype == 'file':
            preprocessing = Preprocessor(filepath)
            preprocessing.experiment_type()
            experiment_type = preprocessing.get_experiment_type()
            
            if 'CV' in experiment_type:
                self.update_status("Processing CV file...")
                self.process_cv(preprocessing, filepath)
                
            elif experiment_type.strip() == 'EISPOT':
                self.update_status("Processing EISPOT file...")
                self.process_eis(preprocessing, filepath)
        
        self.update_status("File processing complete.")
        
    def process_cv(self, preprocessing, filepath):
        preprocessing.pull_cv_metadata()
        custom_curves = self.data_loader.which_curves()
        
        if custom_curves:
            pass
        else:
            curve_data = preprocessing.extract_cv_curves()
            
        surface_area = 0.0000199504 
        analysis = Analysis(curve_data, preprocessing.sampling_rate, surface_area)
        results = analysis.process_curves()
        
        self.visualization.open_save_dialog()
        save_path = self.visualization.get_save_path()
        name = filepath.split('/')[-1]
        self.visualization.output_as_csv(results, preprocessing.vlimit1, preprocessing.vlimit2, name)
        
    def process_eis(self, preprocessing, filepath):
        eis_analysis = EIS_Analysis()
        preprocessing.pull_eis_metadata()
        frequencies = self.data_loader.extra_eis_frequencies()
        dataframe = preprocessing.extract_eis()
        dataframe = dataframe.drop(dataframe.index[0:2])
        frequencies = [1.0, 1000.0, 100000.0, 1000000.0]
        
        if self.data_loader.custom_freq:
            frequencies = frequencies + self.data_loader.additional_frequencies
            
        frequencies.sort()
        closest_frequencies = eis_analysis.get_closest_freq(dataframe, frequencies)
        filtered_df = dataframe[dataframe['Freq'].isin(closest_frequencies)]
        
        self.visualization.open_save_dialog()
        save_path = self.visualization.get_save_path()
        name = filepath.split('/')[-1]
        self.visualization.eis_to_csv(name, filtered_df, preprocessing.notes)
        
    def show_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.update_status(f"Loading CSV: {file_path}")
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                self.tree["columns"] = headers
                for col in headers:
                    self.tree.heading(col, text=col)
                    self.tree.column(col, anchor=tk.CENTER)
                
                for row in self.tree.get_children():
                    self.tree.delete(row)
                    
                for row in reader:
                    self.tree.insert("", tk.END, values=row)
                    
            self.update_status(f"CSV loaded: {file_path}")

    def parse(self):
        # Add your parse logic here
        pass

    def toggle_listbox(self):
        if self.checkbox_var.get():
            if self.listbox is None:
                # Create the Listbox with multiple selection mode
                self.listbox = tk.Listbox(self.cv_frame, selectmode=tk.MULTIPLE, exportselection=False)
                self.listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

                for choice in self.choices:
                    self.listbox.insert(tk.END, choice)

                self.scrollbar = ttk.Scrollbar(self.cv_frame, orient=tk.VERTICAL, command=self.listbox.yview)
                self.scrollbar.grid(row=1, column=1, sticky="ns")
                self.listbox.config(yscrollcommand=self.scrollbar.set)

                self.get_selected_button = ttk.Button(self.cv_frame, text="Get Selected", command=self.get_selected)
                self.get_selected_button.grid(row=2, column=0, columnspan=2, pady=10)

                self.selected_label = ttk.Label(self.cv_frame, text="")
                self.selected_label.grid(row=3, column=0, columnspan=2, pady=10)

                self.cv_frame.columnconfigure(0, weight=1)
                self.cv_frame.rowconfigure(1, weight=1)
            else:
                self.listbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
                self.scrollbar.grid(row=1, column=1, sticky="ns")
                self.get_selected_button.grid(row=2, column=0, columnspan=2, pady=10)
                self.selected_label.grid(row=3, column=0, columnspan=2, pady=10)
        else:
            if self.listbox is not None:
                self.listbox.grid_remove()
                self.scrollbar.grid_remove()
                self.get_selected_button.grid_remove()
                self.selected_label.grid_remove()

    def get_selected(self):
        selected_indices = self.listbox.curselection()
        selected_items = [self.listbox.get(i) for i in selected_indices]
        self.selected_label.config(text="Selected: " + ", ".join(selected_items))

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = App(root)
    app.grid(row=0, column=0, sticky="nsew")
    root.mainloop()
