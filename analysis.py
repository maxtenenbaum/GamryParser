import pandas as pd
import numpy as np
import os

class Analysis:
    def __init__(self, curve_dataframes, sampling_rate, surface_area):
        self.curve_dataframes = curve_dataframes
        self.sampling_rate = sampling_rate
        self.surface_area = surface_area

    def process_curves(self):
        results = []

        for curve, df in self.curve_dataframes.items():
            # Processing each curve as in your original function
            curve_df = df[1::].copy()
            curve_df['A'] = pd.to_numeric(curve_df['A'], errors='coerce')
            curve_df['V vs. Ref.'] = pd.to_numeric(curve_df['V vs. Ref.'], errors='coerce')
            curve_df['Charge'] = 0.0
            curve_df['Charge'][1:] = (curve_df['A'].rolling(window=2).mean()[1:]) * self.sampling_rate * 1000
            curve_df['Total Charge'] = curve_df['Charge'].cumsum()
            curve_df['Charge Density mC/cm2'] = curve_df['Charge'] / self.surface_area
            curve_df['Absolute Charge'] = abs(curve_df['Charge'] / self.surface_area)
            curve_df['Cathodal Integral Value'] = np.where(curve_df['Charge'] < 0, curve_df['Charge Density mC/cm2'], 0)
            curve_df['Anodal Integral Value'] = np.where(curve_df['Charge'] >= 0, curve_df['Charge Density mC/cm2'], 0)

            # Calculating metrics for the curve
            csc_c = abs(curve_df['Cathodal Integral Value'].sum())
            csc_a = abs(curve_df['Anodal Integral Value'].sum())
            total_cathodal_charge = csc_c * self.surface_area * 1000000
            total_anodal_charge = csc_a * self.surface_area * 1000000
            qh = abs(curve_df['Absolute Charge'].sum()) / 2

            # Storing the results
            results.append({
                'Curve #': curve,
                'CSC_A': round(csc_a,3),
                'CSC_C': round(csc_c,3),
                'Total_Anodal_Charge': round(total_anodal_charge,3),
                'Total_Cathodal_Charge': round(total_cathodal_charge,3),
                'Qh': round(qh,3)
            })

        # Convert the results to a DataFrame
        results_df = pd.DataFrame(results)
        return(results_df)
