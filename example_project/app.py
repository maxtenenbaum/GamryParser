import sys
import os
sys.path.append(os.path.abspath(".."))
from gamryparser import Parser
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title='GamryParser', page_icon=":material/network_intel_node:")
st.title("GamryParser – Aging Study Dashboard")

data_folder = r"C:\Users\mtenenba\Desktop\GamryParser\example_project\processed_outputs"

@st.cache_data
def load_csv(file_path):
    return pd.read_csv(file_path)

def render_filters(df, exp_name):
    filters = {}
    with st.expander("🔍 Filter Options", expanded=False):
        if 'Date' in df.columns:
            st.markdown("**Select Dates**")
            dates = sorted(df['Date'].dropna().unique())
            date_cols = st.columns(4)
            selected_dates = []
            for i, d in enumerate(dates):
                col = date_cols[i % 4]
                if col.checkbox(str(d), key=f"{exp_name}_date_{d}", value=True):
                    selected_dates.append(d)
            filters['Date'] = selected_dates

        if 'Site' in df.columns:
            st.markdown("**Select Sites**")
            sites = sorted(df['Site'].dropna().unique())
            site_cols = st.columns(4)
            selected_sites = []
            for i, s in enumerate(sites):
                col = site_cols[i % 4]
                if col.checkbox(str(s), key=f"{exp_name}_site_{s}", value=True):
                    selected_sites.append(s)
            filters['Site'] = selected_sites

        if 'Freq' in df.columns:
            st.markdown("**Frequency Range (Hz)**")
            freq_min, freq_max = float(df['Freq'].min()), float(df['Freq'].max())
            filters['Freq'] = st.slider(
                "", min_value=freq_min, max_value=freq_max,
                value=(freq_min, freq_max), key=f"{exp_name}_freq_slider"
            )
    return filters


def apply_filters(df, filters):
    if 'Date' in filters:
        df = df[df['Date'].isin(filters['Date'])]
    if 'Site' in filters:
        df = df[df['Site'].isin(filters['Site'])]
    if 'Freq' in filters and 'Freq' in df.columns:
        df = df[(df['Freq'] >= filters['Freq'][0]) & (df['Freq'] <= filters['Freq'][1])]
    return df


def render_cv_dashboard(df, exp_name):
    filters = render_filters(df, exp_name)
    df = apply_filters(df, filters)
    tabs = st.tabs(["Plot", "Charge Storage Capacity", "Raw Data"])

    with tabs[0]:
        df['Vf'] = pd.to_numeric(df['Vf'], errors='coerce')
        df['Im'] = pd.to_numeric(df['Im'], errors='coerce')
        fig = go.Figure()
        for site, group in df.groupby('Site'):
            fig.add_trace(go.Scatter(x=group['Vf'], y=group['Im'], mode='lines', name=site))
        fig.update_layout(
            margin=dict(t=10, b=10),
            xaxis_title='Potential (V)',
            yaxis_title='Current (A)',
            yaxis_tickformat="~s",
            yaxis_ticksuffix='A'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Anodal Charge Storage Capacity'] = pd.to_numeric(df['Anodal Charge Storage Capacity'], errors='coerce')
        df['Cathodal Charge Storage Capacity'] = pd.to_numeric(df['Cathodal Charge Storage Capacity'], errors='coerce')

        st.subheader("Anodal CSC")
        fig = go.Figure()
        for site, group in df.groupby("Site"):
            fig.add_trace(go.Scatter(x=group["Date"], y=group["Anodal Charge Storage Capacity"], mode='markers+lines', name=site))
        fig.update_layout(
            margin=dict(t=10, b=10),
            xaxis_title='Date',
            yaxis_title='Anodal Charge Storage Capacity (mC/cm2)',
            yaxis_tickformat="~s"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Cathodal CSC")
        fig2 = go.Figure()
        for device, group in df.groupby("Site"):
            fig2.add_trace(go.Scatter(x=group['Date'], y=group['Cathodal Charge Storage Capacity'], mode='markers+lines', name=device))
        fig2.update_layout(
            margin=dict(t=10, b=10),
            xaxis_title='Date',
            yaxis_title='Cathodal Charge Storage Capacity (mC/cm2)',
            yaxis_tickformat="~s"
        )
        st.plotly_chart(fig2, use_container_width=True)

    with tabs[2]:
        st.dataframe(df, use_container_width=True)


def render_eis_dashboard(df, exp_name):
    filters = render_filters(df, exp_name)
    df = apply_filters(df, filters)
    tabs = st.tabs(["Bode Plot", "Impedance Stability", "Raw Data"])

    with tabs[0]:
        df['Freq'] = pd.to_numeric(df['Freq'], errors='coerce')
        df['Zmod'] = pd.to_numeric(df['Zmod'], errors='coerce')
        df.dropna(subset=['Freq', 'Zmod'], inplace=True)

        fig = go.Figure()
        for site, group in df.groupby("Site"):
            fig.add_trace(go.Scatter(x=group["Freq"], y=group["Zmod"], mode='markers+lines', name=site))
        fig.update_layout(
            margin=dict(t=10, b=10),
            xaxis_title="Frequency (Hz)",
            yaxis_title="|Z| (Ohm)",
            xaxis_type="log",
            yaxis_type="log",
            xaxis_tickformat="~s",
            xaxis_ticksuffix='Hz',
            yaxis_tickformat="~s",
            yaxis_ticksuffix='Ω'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        df['Freq'] = pd.to_numeric(df['Freq'], errors='coerce')
        df['Zmod'] = pd.to_numeric(df['Zmod'], errors='coerce')
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['Freq', 'Zmod', 'Date'], inplace=True)

        freq_options = [0.1, 100, 1000, 10000, 100000]
        selected_freq = st.pills("Select frequency (Hz):", freq_options, default=0.1)

        available_freqs = df['Freq'].dropna().unique()
        closest_freq = available_freqs[np.argmin(np.abs(available_freqs - selected_freq))]

        st.markdown(f"Showing data for closest available frequency: **{closest_freq:.2f} Hz**")

        df_freq = df[df['Freq'] == closest_freq]

        fig = go.Figure()
        for site, group in df_freq.groupby("Site"):
            fig.add_trace(go.Scatter(x=group["Date"], y=group["Zmod"], mode='markers+lines', name=site))
        fig.update_layout(
            margin=dict(t=20, b=10),
            xaxis_title="Date",
            yaxis_title="|Z| (Ohm)",
            yaxis_type="log",
            yaxis_tickformat="~s",
            yaxis_ticksuffix='Ω'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        st.dataframe(df, use_container_width=True)


# Main loop
for exp_file in os.listdir(data_folder):
    st.markdown("---")
    exp_name = exp_file.split('.')[0]
    st.subheader(exp_name)
    df = load_csv(os.path.join(data_folder, exp_file))
    if 'cv' in exp_file.lower():
        render_cv_dashboard(df, exp_name)
    elif 'eis' in exp_file.lower():
        render_eis_dashboard(df, exp_name)
