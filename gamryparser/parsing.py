import os
import csv
import pandas as pd

class Parser():
    def __init__(self, filepath, lines, experiment, dataframes, scanrate, stepsize, surface_area):
        self.filepath = filepath
        self.scanrate = scanrate
        self.stepsize = stepsize
        self.surface_area = surface_area
        self.lines = lines
        self.experiment = experiment
        self.notes = ''
        self.dataframes = dataframes

    @classmethod
    def from_file(cls, filepath, surface_area=2000):
        scanrate = None
        stepsize = None

        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                lines = file.readlines()
        except UnicodeDecodeError:
            with open(filepath, 'r', encoding='ISO-8859-1') as file:
                lines = file.readlines()

        experiment = ""
        for line in lines:
            split_line = line.split('\t')
            if split_line[0] == "TAG":
                experiment = split_line[-1].strip()
            elif split_line[0] == 'SCANRATE':
                try:
                    scanrate = float(split_line[-2].strip())
                except (ValueError, IndexError):
                    scanrate = None
            elif split_line[0] == 'STEPSIZE':
                try:
                    stepsize = float(split_line[-2].strip())
                except (ValueError, IndexError):
                    stepsize = None

        dataframes = cls.parse_tables_from_lines(lines, experiment, scanrate, stepsize, surface_area)

        return cls(filepath, lines, experiment, dataframes, scanrate, stepsize, surface_area)


    @staticmethod
    def parse_tables_from_lines(lines, experiment, scanrate, stepsize, surface_area):
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        split_rows = [row.split('\t') for row in cleaned_lines]
        lines_dataframe = pd.DataFrame(split_rows)

        # Identify all 'TABLE' row indices
        table_indices = lines_dataframe[
            lines_dataframe.apply(lambda row: row.astype(str).str.contains('TABLE').any(), axis=1)
        ].index.tolist()
        table_indices.append(len(lines_dataframe))  # Ensure last section is captured

        # Split into chunks
        split_data = {}
        for i in range(len(table_indices) - 1):
            start = table_indices[i]
            end = table_indices[i + 1]
            chunk = lines_dataframe.iloc[start:end].reset_index(drop=True)
            name = str(chunk.iloc[0, 0].split('\t')[0])
            split_data[name] = chunk

        # Parse each chunk
        dataframes = {}
        for name, df in split_data.items():
            try:
                header_row_index = df[df.iloc[:, 0] == 'Pt'].index[0]
                headers = df.iloc[header_row_index].astype(str)
                data = df.iloc[header_row_index + 1:].reset_index(drop=True)
                data.columns = headers
                data = data.loc[:, data.columns.notna()]
                data = data.loc[:, data.columns.str.strip() != ""]
                data = data.loc[:, data.columns != "None"]

                def starts_with_digit(val):
                    return isinstance(val, str) and val.strip() and val.strip()[0].isdigit()

                valid_rows = data[data.iloc[:, 0].apply(starts_with_digit)].reset_index(drop=True)

                if experiment.lower() == 'cv' and name[:5] == 'CURVE':
                    valid_rows['Im'] = valid_rows['Im'].astype(float)
                    if scanrate is not None and stepsize is not None:
                        dt = stepsize / scanrate
                        valid_rows['Charge'] = (((valid_rows['Im'] + valid_rows['Im'].shift(1)) / 2) * dt) * 1000
                        valid_rows['Charge'] = valid_rows['Charge'].fillna(0)
                        valid_rows['Total Charge'] = valid_rows['Charge'].cumsum()
                        valid_rows['Charge Density'] = valid_rows['Total Charge'] / (surface_area * 1e-8)
                        valid_rows['Charge Integral'] = abs(valid_rows['Charge']) / (surface_area * 1e-8)
                        valid_rows['Anodal Charge Integral'] = valid_rows['Charge Integral'].where(valid_rows['Charge'] > 0, 0)
                        valid_rows['Cathodal Charge Integral'] = valid_rows['Charge Integral'].where(valid_rows['Charge'] < 0, 0)
                    else:
                        print("Missing scanrate or stepsize — skipping charge calculations.")

                dataframes[name] = valid_rows

            except IndexError as e:
                print(f"Skipping {name}, {str(e)}")


        return dataframes

    def get_dataframe_names(self):
        return list(self.dataframes.keys())
    
    def save_dataframes(self, save_path):
        os.makedirs(save_path, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(self.filepath))[0]

        for name, df in self.dataframes.items():
            filename = f"{base_name}_{name}.csv"
            full_path = os.path.join(save_path, filename)
            try:
                df.to_csv(full_path, index=False)
                print(f"Saved {filename}")
            except Exception as e:
                print(f"Failed to save {filename}: {e}")
    
    def save_dataframe(self, name, save_path):
        if name not in self.dataframes:
            print(f"No dataframe named '{name}' found.")
            return
        os.makedirs(save_path, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(self.filepath))[0]
        filename = f"{base_name}_{name}.csv"
        full_path = os.path.join(save_path, filename)
        try:
            self.dataframes[name].to_csv(full_path, index=False)
            print(f"Saved {filename}")
        except Exception as e:
            print(f"Failed to save {filename}: {e}")

    def get_experiment_type(self):
        return self.experiment

    def __str__(self):
        tables = ", ".join(self.get_dataframe_names())
        return f"Parser for '{os.path.basename(self.filepath)}' with tables: [{tables}]"

    def __repr__(self):
        return f"<Parser(filepath='{self.filepath}', tables={len(self.dataframes)})>"

    def __getitem__(self, key):
        return self.dataframes[key]

    def __len__(self):
        return len(self.dataframes)
