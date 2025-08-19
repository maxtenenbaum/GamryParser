import pandas as pd
import numpy as np
import os

class Analyzer:
    def __init__(self, source, table_name=None):
        self.experiment = None  # default

        if isinstance(source, str) and source.endswith('.csv'):
            self.df = pd.read_csv(source)
            self.source = source
            self.label = os.path.splitext(os.path.basename(source))[0]

        elif hasattr(source, 'dataframes'):  # likely a Parser object
            if table_name is None:
                raise ValueError("When passing a Parser, you must specify the table_name.")
            self.df = source[table_name]
            self.source = f"{source.filepath}:{table_name}"
            self.label = table_name
            self.experiment = getattr(source, 'experiment', None)  # ✅ grab the experiment

        else:
            raise TypeError("source must be a CSV filepath or a Parser object.")

        for col in self.df.columns:
            try:
                self.df[col] = pd.to_numeric(self.df[col])
            except (ValueError, TypeError):
                pass

class EISAnalyzer(Analyzer):
    """
    Analyzer subclass for Electrochemical Impedance Spectroscopy (EIS) data.
    Provides impedance- and phase-based metrics.
    """
    def __init__(self, source, table_name=None):
        super().__init__(source, table_name)
        if not (self.experiment and self.experiment.upper().strip() == 'EISPOT'):
            raise ValueError("This dataset is not tagged as EISPOT (EIS data).")

    def get_impedance_at_freq(self, freq=1000):
        idx = (self.df['Freq'] - freq).abs().idxmin()
        row = self.df.loc[idx]
        return row['Zmod'], row['Zphz']

    def get_solution_resistance(self):
        high_freq = self.df['Freq'].max()
        row = self.df[self.df['Freq'] == high_freq].iloc[0]
        return row['Zreal']

    def estimate_rct(self):
        return abs(self.df['Zreal'].max() - self.df['Zreal'].min())

    def log_log_slope(self):
        log_f = self.df['Freq'].apply(np.log10)
        log_z = self.df['Zmod'].apply(np.log10)
        slope, *_ = np.polyfit(log_f, log_z, 1)
        return slope

    def summary(self, freq=1000):
        zmod, zphz = self.get_impedance_at_freq(freq)
        rs = self.get_solution_resistance()
        rct = self.estimate_rct()
        slope = self.log_log_slope()
        return {
            "Source": self.source,
            f"Zmod @ {freq} Hz (Ω)": zmod,
            f"Phase @ {freq} Hz (°)": zphz,
            "Rs (Ω)": rs,
            "Estimated Rct (Ω)": rct,
            "log-log slope": slope
        }

class CVAnalyzer(Analyzer):
    def __init__(self, source, table_name=None):
        super().__init__(source, table_name)
        if not (self.experiment and self.experiment.upper() == 'CV'):
            raise ValueError("This dataset is not tagged as CV.")

    def get_csc_cathodal(self):
        return sum(self.df['Cathodal Charge Integral'])
    
    def get_csc_anodal(self):
        return sum(self.df['Anodal Charge Integral'])

