import pandas as pd
import numpy as np
import os

class Analyzer:
    """
    Base class for analyzing electrochemical data.
    Accepts either a CSV file or a Parser object with a table name.
    """

    def __init__(self, source, table_name=None):
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
        else:
            raise TypeError("source must be a CSV filepath or a Parser object.")

        for col in self.df.columns:
            try:
                self.df[col] = pd.to_numeric(self.df[col])
            except (ValueError, TypeError):
                pass

    def is_eis(self):
        """Check if the dataset contains EIS columns."""
        required_cols = {'Freq', 'Zreal', 'Zimag', 'Zmod', 'Zphz'}
        return required_cols.issubset(self.df.columns)

class EISAnalyzer(Analyzer):
    """
    Analyzer subclass for Electrochemical Impedance Spectroscopy (EIS) data.
    Provides impedance- and phase-based metrics.
    """

    def __init__(self, source, table_name=None):
        super().__init__(source, table_name)
        if not self.is_eis():
            raise ValueError("This dataset does not contain the required EIS columns.")

    def get_impedance_at_freq(self, freq=1000):
        """Return (Zmod, Zphz) at the closest frequency to `freq`."""
        idx = (self.df['Freq'] - freq).abs().idxmin()
        row = self.df.loc[idx]
        return row['Zmod'], row['Zphz']

    def get_solution_resistance(self):
        """Return Rs as Zreal at the highest frequency."""
        high_freq = self.df['Freq'].max()
        row = self.df[self.df['Freq'] == high_freq].iloc[0]
        return row['Zreal']

    def estimate_rct(self):
        """Estimate charge transfer resistance as the width of Nyquist arc."""
        return abs(self.df['Zreal'].max() - self.df['Zreal'].min())

    def log_log_slope(self):
        """Slope of log(Zmod) vs log(Freq) across all data."""
        log_f = self.df['Freq'].apply(np.log10)
        log_z = self.df['Zmod'].apply(np.log10)
        slope, *_ = np.polyfit(log_f, log_z, 1)
        return slope

    def summary(self, freq=1000):
        """Return a summary dictionary of EIS metrics."""
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


        """Summary of CSC and peak metrics over the whole sweep."""
        vmin, vmax = self.get_voltage_window()
        (v_an, i_an), (v_ca, i_ca) = self.get_peak_currents()
        csc_ca = self.calculate_csc(polarity='cathodic')
        csc_an = self.calculate_csc(polarity='anodic')

        label_unit = "mC/cm²" if self.area_cm2 else "mC"

        return {
            "Source": self.source,
            "Voltage window (V)": (vmin, vmax),
            "Anodic peak (V, A)": (v_an, i_an),
            "Cathodic peak (V, A)": (v_ca, i_ca),
            f"Cathodic CSC ({label_unit})": csc_ca,
            f"Anodic CSC ({label_unit})": csc_an
        }
