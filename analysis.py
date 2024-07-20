import pandas as pd
import numpy as np
import os
import preprocessing

class Analysis:
    def __init__(self, curve_dataframes, sampling_rate, surface_area, extra_data):
        self.curve_dataframes = curve_dataframes
        self.sampling_rate = sampling_rate
        self.surface_area = surface_area
        self.extra_data = extra_data

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
                'CSC_A': round(csc_a, 3),
                'CSC_C': round(csc_c, 3),
                'Total_Anodal_Charge': round(total_anodal_charge, 3),
                'Total_Cathodal_Charge': round(total_cathodal_charge, 3),
                'Qh': round(qh, 3),
            })

        # Convert the results to a DataFrame
        results_df = pd.DataFrame(results)
        
        # Creating the DataFrame for extra_data
        extra_data_df = pd.DataFrame(self.extra_data[['V vs. Ref.', 'A']]).iloc[1:]
        
        # Merging the two DataFrames
        combined_df = pd.concat([results_df, extra_data_df], axis=1)
        
        return combined_df

class EIS_Analysis:
    def __init__(self):
        self.real_frequencies = None

    def find_closest(self, series, number):
        # Ensure the series is numeric
        numeric_series = pd.to_numeric(series, errors='coerce')
        # Find the index of the closest value
        idx = (numeric_series - number).abs().argmin()
        return numeric_series.iloc[idx]
    
    def get_closest_freq(self, df, frequencies):
        # Ensure 'Freq' column is in numeric format
        if not pd.api.types.is_numeric_dtype(df['Freq']):
            df['Freq'] = pd.to_numeric(df['Freq'], errors='coerce')
        
        # Find the closest frequencies
        self.real_frequencies = [self.find_closest(df['Freq'], freq) for freq in frequencies]

        return self.real_frequencies




"""
IF SHOW ALL RAW COLUMNS

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
            'CSC_A': round(csc_a, 3),
            'CSC_C': round(csc_c, 3),
            'Total_Anodal_Charge': round(total_anodal_charge, 3),
            'Total_Cathodal_Charge': round(total_cathodal_charge, 3),
            'Qh': round(qh, 3),
        })

    # Convert the results to a DataFrame
    results_df = pd.DataFrame(results)
    
    # Creating the DataFrame for extra_data
    extra_data_df = pd.DataFrame(self.extra_data)
    
    # Merging the two DataFrames
    combined_df = pd.concat([results_df, extra_data_df], axis=1)
    
    return combined_df


"""