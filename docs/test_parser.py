import pandas as pd

class Parser:
    def __init__(self, lines, experiment, dataframes, scanrate=None, stepsize=None, surface_area=2000):
        self.lines = lines
        self.experiment = experiment
        self.scanrate = scanrate
        self.stepsize = stepsize
        self.surface_area = surface_area
        self.dataframes = dataframes

    @classmethod
    def from_text(cls, filetext, surface_area=2000):
        lines = filetext.splitlines()
        experiment = ""
        scanrate = None
        stepsize = None

        for line in lines:
            split_line = line.split('\t')
            if split_line[0] == "TAG":
                experiment = split_line[-1].strip()
            elif split_line[0] == "SCANRATE":
                try:
                    scanrate = float(split_line[-2].strip())
                except:
                    pass
            elif split_line[0] == "STEPSIZE":
                try:
                    stepsize = float(split_line[-2].strip())
                except:
                    pass

        dataframes = cls.parse_tables_from_lines(lines, experiment, scanrate, stepsize, surface_area)
        return cls(lines, experiment, dataframes, scanrate, stepsize, surface_area)

    @staticmethod
    def parse_tables_from_lines(lines, experiment, scanrate, stepsize, surface_area):
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        split_rows = [row.split('\t') for row in cleaned_lines]
        df = pd.DataFrame(split_rows)

        table_indices = df[
            df.apply(lambda row: row.astype(str).str.contains('TABLE').any(), axis=1)
        ].index.tolist()
        table_indices.append(len(df))

        split_data = {}
        for i in range(len(table_indices) - 1):
            start = table_indices[i]
            end = table_indices[i + 1]
            chunk = df.iloc[start:end].reset_index(drop=True)
            name = str(chunk.iloc[0, 0])
            split_data[name] = chunk

        dataframes = {}
        stats_rows = []

        for name, chunk in split_data.items():
            try:
                header_row = chunk[chunk.iloc[:, 0] == "Pt"].index[0]
                headers = chunk.iloc[header_row].astype(str)
                data = chunk.iloc[header_row + 1:].reset_index(drop=True)
                data.columns = headers

                def starts_with_digit(val):
                    return isinstance(val, str) and val.strip() and val.strip()[0].isdigit()

                valid_rows = data[data.iloc[:, 0].apply(starts_with_digit)].reset_index(drop=True)

                if experiment.lower() == 'cv' and name[:5].upper() == 'CURVE':
                    valid_rows['Im'] = pd.to_numeric(valid_rows['Im'], errors='coerce')

                    if scanrate is not None and stepsize is not None:
                        dt = stepsize / scanrate
                        valid_rows['Charge'] = (((valid_rows['Im'] + valid_rows['Im'].shift(1)) / 2) * dt) * 1000
                        valid_rows['Charge'] = valid_rows['Charge'].fillna(0)
                        valid_rows['Total Charge'] = valid_rows['Charge'].cumsum()
                        valid_rows['Charge Density'] = valid_rows['Total Charge'] / (surface_area * 1e-9)
                        valid_rows['Charge Integral'] = abs(valid_rows['Charge']) / (surface_area * 1e-9)
                        valid_rows['Anodal Charge Integral'] = valid_rows['Charge Integral'].where(valid_rows['Charge'] > 0, 0)
                        valid_rows['Cathodal Charge Integral'] = valid_rows['Charge Integral'].where(valid_rows['Charge'] < 0, 0)

                        CSCa = valid_rows['Anodal Charge Integral'].sum()
                        CSCc = valid_rows['Cathodal Charge Integral'].sum()
                        stats_rows.append({'Curve Name': name, 'CSCa (C/cm²)': CSCa, 'CSCc (C/cm²)': CSCc})

                dataframes[name] = valid_rows
            except Exception:
                continue

        # If stats were gathered, add the Stats dataframe
        if stats_rows:
            stats_df = pd.DataFrame(stats_rows)
            dataframes['Stats'] = stats_df

        return dataframes


def analyze_file(filetext, surface_area=2000):
    parser = Parser.from_text(filetext, surface_area=surface_area)
    output = {}
    for name, df in parser.dataframes.items():
        output[name] = df.to_html(classes='dataframe', border=0)
    return output

def get_csvs(filetext, surface_area=2000):
    parser = Parser.from_text(filetext, surface_area=surface_area)
    return {name: df.to_csv(index=False) for name, df in parser.dataframes.items()}
