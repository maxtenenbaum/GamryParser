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
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator

class App(tk.Frame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.root = master
        self.root.title("GamryParser")
        self.root.set_theme("arc")
        self.root.geometry("1440x1080")
        
        self.data_loader = DataLoading()
        self.visualization = Visualization()

        # Mainframe
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Resize settings
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

        self.filepath = None
        self.choices = []
        self.canvas = None
        self.fig = None

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        self.update_status("Ready")

        """Left Side"""
        # Left side frame
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, rowspan=3, sticky=(tk.N, tk.W), padx=10, pady=10)

        # Load File Frame
        self.button_frame = ttk.Frame(self.left_frame)
        self.button_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Load file button
        self.load_button = ttk.Button(self.button_frame, text="Load File", command=self.load_file)
        self.load_button.grid(row=0, column=0, padx=0, pady=5, sticky=(tk.W))

        # Load folder button
        self.load_folder = ttk.Button(self.button_frame, text="Load Folder", command=self.load_folder)
        self.load_folder.grid(row=0, column=0, padx=0, pady=5, sticky=(tk.E))

        """ SETTING FRAMES """
        # Frame for general settings
        self.general_frame = ttk.Labelframe(self.button_frame, text="Electrosite Surface Area (cm\u00B2)")
        self.general_frame.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Frame for CV settings
        self.cv_frame = ttk.Labelframe(self.button_frame, text="CV Settings")
        self.cv_frame.grid(row=2, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        # Frame for EIS settings
        self.eis_frame = ttk.Labelframe(self.button_frame, text='EIS Settings')
        self.eis_frame.grid(row=3, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        """ GENERAL SETTINGS """
        self.surface_area_input = ttk.Entry(self.general_frame)
        self.surface_area_input.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.default_SA = '0.0000199504'
        self.surface_area_input.insert(0, self.default_SA)

        """ CV SETTINGS """
        self.extra_curves_var = tk.BooleanVar()
        self.extra_curves_box = ttk.Checkbutton(self.cv_frame, text="Custom Select Curves", variable=self.extra_curves_var, command=self.show_extra_curves)
        self.extra_curves_box.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.listbox = None
        self.extra_curves_box.config(state='disabled')
        self.selected_curves = None

        self.plot_cv_var = tk.BooleanVar()
        self.plot_cv_button = ttk.Checkbutton(self.cv_frame, text="Plot CV", variable=self.plot_cv_var, command=self.plot_cv)
        self.plot_cv_button.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.plot_cv_button.config(state="disabled")

        """EIS SETTINGS"""
        self.custom_freq_var = tk.BooleanVar()
        self.custom_freq_box = ttk.Checkbutton(self.eis_frame, text="Custom Select Frequencies", variable=self.custom_freq_var, command=self.show_extra_freqs)
        self.custom_freq_box.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.customfreq_entry = None
        self.custom_freq_box.config(state='disabled')

        self.plot_eis_var = tk.BooleanVar()
        self.plot_eis_button = ttk.Checkbutton(self.eis_frame, text="Plot EIS", variable=self.plot_eis_var, command=self.plot_eis)
        self.plot_eis_button.grid(row=2, column=0, padx=5, pady=5, stick=(tk.W, tk.E))
        self.plot_eis_button.config(state='disabled')

        self.get_all_frequencies_var = tk.BooleanVar()
        self.get_all_frequencies_box = ttk.Checkbutton(self.eis_frame, text="Get All Frequencies", variable=self.get_all_frequencies_var, command=self.get_all_frequencies)
        self.get_all_frequencies_box.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.get_all_frequencies_box.configure(state='disabled')

        # Parse File button
        self.parse_button = ttk.Button(self.button_frame, text="Parse File", command=self.parse_file)
        self.parse_button.grid(row=4, column=0, padx=5, pady=5, stick=(tk.W, tk.E))
        self.parse_button.config(state='disabled')

        # Parse Folder button
        self.parse_folder = ttk.Button(self.button_frame, text="Parse Folder", command=self.parse_folder)
        self.parse_folder.grid(row=5, column=0, padx=5, pady=5, stick=(tk.W, tk.E))
        self.parse_folder.config(state='disabled')

        # Reset button
        self.reset_button = ttk.Button(self.button_frame, text="Reset", command=self.reset)
        self.reset_button.grid(row=6, column=0, padx=5, pady=5, sticky=(tk.E, tk.W))


        """ PLOTTING """
        self.plot_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        self.plot_frame.grid(row=0, column=1, padx=20, pady=10, rowspan=3, stick=(tk.N, tk.S, tk.E, tk.W))

    def plot_cv(self, dataframe):
        x = dataframe['V vs. Ref.']
        x = pd.to_numeric(x, errors='coerce')
        y = dataframe['A']
        y = pd.to_numeric(y, errors='coerce')
        fig, ax = plt.subplots()
        ax.plot(x, y, marker='o', linestyle='', markersize=4, color='blue', alpha=0.7)
        ax.set_xlabel('V vs. Ref.')
        ax.set_ylabel('A')
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def plot_eis(self, dataframe):
        x = dataframe['Freq']
        x = pd.to_numeric(x, errors='coerce')
        y1 = dataframe['Zmod']
        y1 = pd.to_numeric(y1, errors='coerce')
        y2 = dataframe['Zphz']
        y2 = pd.to_numeric(y2, errors='coerce')
        fig, ax = plt.subplots()
        ax.plot(x, y1, marker='o', linestyle='-', label='Impedence')
        ax.plot(x, y2, marker='x', linestyle='--', label='Phase Angle')
        ax.set_xlabel('Frequency (Hz)')
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
        self.canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def get_all_frequencies(self):
        self.root.update_idletasks()

    def update_status(self, message):
        self.status_var.set(message)
        self.root.update_idletasks()

    def load_file(self):
        self.update_status("Loading file...")
        self.data_loader.open_file_dialog()
        self.filepath = self.data_loader.get_file_path()
        self.update_status(f'Loaded: {self.filepath}')
        self.parse_button.config(state='normal')
        preprocessor = Preprocessor(self.filepath)
        experiment = preprocessor.experiment_type()
        experiment_type = preprocessor.get_experiment_type()
        if "CV" in experiment_type:
            preprocessor.pull_cv_metadata()
            curve_data = preprocessor.extract_cv_curves()
            self.choices = preprocessor.extract_cv_curves(get_curves=False)
            self.extra_curves_box.config(state='normal')
            self.custom_freq_box.config(state='disabled')
            self.plot_cv_button.config(state='normal')
            self.plot_eis_button.config(state='disabled')
            self.get_all_frequencies_box.config(state='disabled')

            self.root.update_idletasks()
        elif experiment_type.strip() == 'EISPOT':
            preprocessor.pull_eis_metadata()
            self.custom_freq_box.config(state='normal')
            self.extra_curves_box.config(state='disabled')
            self.plot_cv_button.config(state='disabled')
            self.plot_eis_button.config(state='normal')
            self.get_all_frequencies_box.config(state='normal')

    def load_folder(self):
        self.update_status("Loading folder...")
        self.data_loader.open_folder_dialog()
        self.filepath = self.data_loader.get_file_path()
        self.update_status(f'Loaded: {self.filepath}')
        self.extra_curves_box.config(state='normal')
        self.custom_freq_box.config(state='normal')
        self.parse_folder.config(state='normal')
        self.get_all_frequencies_box.config(state='normal')

    def show_extra_curves(self):
        if self.extra_curves_var.get():
            if self.listbox is None:
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
        self.selected_curves = selected_items
        print(type(self.selected_curves))

    def show_extra_freqs(self):
        default_frequencies = '1.0, 1000.0, 100000.0, 1000000.0'
        if self.custom_freq_var.get():
            if self.customfreq_entry is None:
                self.customfreq_entry = ttk.Entry(self.eis_frame)
                self.customfreq_entry.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
                self.customfreq_entry.insert(0, default_frequencies)
        else:
            if self.customfreq_entry is not None:
                self.customfreq_entry.grid_remove()

    def parse_file(self):
        filepath = self.filepath
        preprocessing = Preprocessor(filepath)
        preprocessing.experiment_type()
        experiment_type = preprocessing.get_experiment_type()
        visualization = Visualization()
        if 'CV' in experiment_type:
            preprocessing.pull_cv_metadata()
            curve_data = preprocessing.extract_cv_curves()
            surface_area = float(self.surface_area_input.get())
            analysis = Analysis(curve_data, preprocessing.sampling_rate, surface_area)
            results = analysis.process_curves()
            if self.extra_curves_var.get():
                for curve in results['Curve #']:
                    if curve not in self.selected_curves:
                        results.drop(index=results.loc[results['Curve #'] == curve].index[0], inplace=True)
            full_df = preprocessing.extract_cv_curves(get_curves=True)
            extra_df = full_df[['V vs. Ref.','A']]
            extra_df = extra_df.drop(extra_df.index[0]).reset_index(drop=True)
            results = pd.concat([results, extra_df[['V vs. Ref.','A']]], axis=1)
            if self.plot_cv_var.get():
                if self.canvas is not None:
                    self.canvas.get_tk_widget().pack_forget()
                    self.canvas.get_tk_widget().destroy()
                    plt.close(self.fig)  # Close the figure
                    self.canvas = None
                    self.fig = None
                self.plot_cv(full_df)
            visualization.open_save_dialog()
            save_path = visualization.get_save_path()
            name = filepath.split('/')[-1]
            visualization.output_as_csv(results, preprocessing.vlimit1, preprocessing.vlimit2, name)
        elif experiment_type.strip() == 'EISPOT':
            eis_analysis = EIS_Analysis()
            preprocessing.pull_eis_metadata()
            if self.custom_freq_var.get():
                frequencies = [float(freq.strip()) for freq in self.customfreq_entry.get().split(',')]
                dataframe = preprocessing.extract_eis(extra_data=False)
                dataframe = dataframe.drop(dataframe.index[0:2])
                frequencies.sort()
                closest_frequencies = eis_analysis.get_closest_freq(dataframe, frequencies)
                filtered_df = dataframe[dataframe["Freq"].isin(closest_frequencies)]
                new_df = pd.DataFrame(' ', index=dataframe.index, columns=dataframe.columns)
                new_df.iloc[:len(filtered_df)] = filtered_df.values
                new_df['Zmod_Full'] = dataframe['Zmod']
                new_df['Zphz_Full'] = dataframe['Zphz']
            elif self.get_all_frequencies_var.get():
                new_df = preprocessing.extract_eis()
                new_df = new_df.drop(new_df.index[0:2])
            else:
                frequencies = [1.0, 1000.0, 100000.0, 1000000.0]
                dataframe = preprocessing.extract_eis(extra_data=False)
                dataframe = dataframe.drop(dataframe.index[0:2])
                frequencies.sort()
                closest_frequencies = eis_analysis.get_closest_freq(dataframe, frequencies)
                filtered_df = dataframe[dataframe["Freq"].isin(closest_frequencies)]
                new_df = pd.DataFrame(' ', index=dataframe.index, columns=dataframe.columns)
                new_df.iloc[:len(filtered_df)] = filtered_df.values
                new_df['Zmod_Full'] = dataframe['Zmod']
                new_df['Zphz_Full'] = dataframe['Zphz']
            if self.plot_eis_var.get():
                if self.canvas is not None:
                    self.canvas.get_tk_widget().pack_forget()
                    self.canvas.get_tk_widget().destroy()
                    plt.close(self.fig)  # Close the figure
                    self.canvas = None
                    self.fig = None
                self.plot_eis(new_df)
            visualization.open_save_dialog()
            save_path = visualization.get_save_path()
            name = filepath.split('/')[-1]
            visualization.eis_to_csv(name, new_df, preprocessing.notes)
        
        self.update_status("File processing complete.")

    def parse_folder(self):
        visualization = Visualization()
        filepath = self.filepath
        for file in os.listdir(filepath):
            base, ext = os.path.splitext(file)
            if ext.lower() == '.dta':
                full_path = os.path.join(filepath, file)     
                preprocessing = Preprocessor(full_path)
                preprocessing.experiment_type()
                experiment_type = preprocessing.get_experiment_type()
                saveway = f"{filepath}/{file}"

                if 'CV' in experiment_type:
                    preprocessing.pull_cv_metadata()
                    curve_data = preprocessing.extract_cv_curves()
                    surface_area = float(self.surface_area_input.get())
                    analysis = Analysis(curve_data, preprocessing.sampling_rate, surface_area)
                    results = analysis.process_curves()
                    if self.extra_curves_var.get():
                        for curve in results['Curve #']:
                            if curve not in self.selected_curves:
                                results.drop(index=results.loc[results['Curve #'] == curve].index[0], inplace=True)
                    full_df = preprocessing.extract_cv_curves(get_curves=True)
                    extra_df = full_df[['V vs. Ref.','A']]
                    extra_df = extra_df.drop(extra_df.index[0]).reset_index(drop=True)
                    results = pd.concat([results, extra_df[['V vs. Ref.','A']]], axis=1)
                    visualization.output_all_to_csv(results, preprocessing.vlimit1, preprocessing.vlimit2, saveway)
                elif experiment_type.strip() == 'EISPOT':
                    eis_analysis = EIS_Analysis()
                    preprocessing.pull_eis_metadata()
                    if self.custom_freq_var.get():
                        frequencies = [float(freq.strip()) for freq in self.customfreq_entry.get().split(',')]
                    elif not self.custom_freq_var.get():
                        frequencies = [1.0, 1000.0, 100000.0, 1000000.0]
                    dataframe = preprocessing.extract_eis(extra_data=False)
                    dataframe = dataframe.drop(dataframe.index[0:2])
                    frequencies.sort()
                    closest_frequencies = eis_analysis.get_closest_freq(dataframe, frequencies)
                    filtered_df = dataframe[dataframe["Freq"].isin(closest_frequencies)]
                    new_df = pd.DataFrame(' ', index=dataframe.index, columns=dataframe.columns)
                    new_df.iloc[:len(filtered_df)] = filtered_df.values
                    new_df['Zmod_Full'] = dataframe['Zmod']
                    new_df['Zphz_Full'] = dataframe['Zphz']
                    visualization.all_eis_to_csv(saveway, new_df, preprocessing.notes)
            
        self.update_status("File processing complete.")

    def reset(self):
        self.filepath = None
        self.choices = []
        self.canvas = None
        self.fig = None

        self.surface_area_input.delete(0, tk.END)
        self.surface_area_input.insert(0, self.default_SA)
        
        self.extra_curves_var.set(False)
        self.plot_cv_var.set(False)
        self.custom_freq_var.set(False)
        self.plot_eis_var.set(False)
        self.get_all_frequencies_var.set(False)

        self.extra_curves_box.config(state='disabled')
        self.plot_cv_button.config(state='disabled')
        self.custom_freq_box.config(state='disabled')
        self.plot_eis_button.config(state='disabled')
        self.get_all_frequencies_box.config(state='disabled')
        self.parse_button.config(state='disabled')
        self.parse_folder.config(state='disabled')

        if self.listbox is not None:
            self.listbox.destroy()
            self.listbox = None

        if self.customfreq_entry is not None:
            self.customfreq_entry.destroy()
            self.customfreq_entry = None

        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        self.update_status("Ready")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = App(root)
    app.grid(row=0, column=0, sticky="nsew")
    root.mainloop()
