import pandas as pd
from io import StringIO

class Parser:
    def __init__(self, lines, experiment, dataframes):
        self.lines = lines
        self.experiment = experiment
        self.dataframes = dataframes

    @classmethod
    def from_text(cls, filetext):
        lines = filetext.splitlines()
        experiment = ""
        for line in lines:
            split_line = line.split('\t')
            if split_line[0] == "TAG":
                experiment = split_line[-1].strip()
        dataframes = cls.parse_tables_from_lines(lines)
        return cls(lines, experiment, dataframes)

    @staticmethod
    def parse_tables_from_lines(lines):
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
        for name, chunk in split_data.items():
            try:
                header_row = chunk[chunk.iloc[:, 0] == "Pt"].index[0]
                headers = chunk.iloc[header_row].astype(str)
                data = chunk.iloc[header_row + 1:].reset_index(drop=True)
                data.columns = headers
                dataframes[name] = data

                def starts_with_digit(val):
                    return isinstance(val, str) and val.strip() and val.strip()[0].isdigit()
                
                valid_rows = data[data.iloc[:, 0].apply(starts_with_digit)].reset_index(drop=True)

                dataframes[name] = valid_rows
                
            except Exception as e:
                continue
        return dataframes

def analyze_file(filetext):
    parser = Parser.from_text(filetext)
    output = {}
    for name, df in parser.dataframes.items():
        output[name] = df.to_html(classes='dataframe', border=0)
    return output

def get_csvs(filetext):
    parser = Parser.from_text(filetext)
    return {name: df.to_csv(index=False) for name, df in parser.dataframes.items()}



