import os
import pandas as pd

class Preprocessor():
    def __init__(self, filepath):
        self.filepath = filepath
        self.experiment = None
        self.scan_rate = 0.0
        self.step_size = 0.0
        self.vlimit1 = 0.0
        self.vlimit2 = 0.0
        self.sampling_rate = 0.0
    
    def experiment_type(self):
        with open(self.filepath, 'r') as file:
            lines = file.readlines()
        for line in lines:
            split_line = line.split('\t')
            if split_line[0] == "TAG":
                self.experiment = split_line[-1]

    def get_experiment_type(self):
        return self.experiment

    def pull_cv_metadata(self):
        with open(self.filepath, 'r') as file:
            lines = file.readlines()
        file_name = os.path.basename(self.filepath)
        date, time = lines[3].split('\t')[2], lines[4].split('\t')[2]
        for line in lines:
            split_line = line.split('\t')
            #key, value = split_line[0], split_line[2]
            if split_line[0] == "SCANRATE":
                self.scan_rate = float(split_line[2])
            elif split_line[0] == "STEPSIZE":
                self.step_size = float(split_line[2])
            elif split_line[0] == "VLIMIT1":
                self.vlimit1 = float(split_line[2])
            elif split_line[0] == "VLIMIT2":
                self.vlimit2 = float(split_line[2])
        self.sampling_rate = self.step_size / self.scan_rate if self.scan_rate else 0


    def extract_cv_curves(self):
        with open(self.filepath, 'r') as file:
            lines = file.readlines()

        curve_data = {}
        data_section = False
        headers = []
        current_curve = None

        for line in lines:
            if line.strip().startswith('CURVE') and line.strip().endswith('TABLE'):
                current_curve = line.strip().split('\t')[0]
                data_section = True
                curve_data[current_curve] = []
                continue

            if data_section:
                if line.startswith('\t#'):
                    headers = line.strip().split('\t')[1:]
                elif line.startswith('\t'):
                    values = line.strip().split('\t')[1:]
                    if len(values) == len(headers):
                        curve_data[current_curve].append(values)

        for curve in curve_data:
            curve_df = pd.DataFrame(curve_data[curve], columns=headers)
            curve_df = curve_df.apply(pd.to_numeric, errors='ignore')
            curve_data[curve] = curve_df[['V vs. Ref.', 'A']]

        print(f"\nNumber of curves found: {len(curve_data)}")
        print("Curves:", list(curve_data.keys()))

        return curve_data
