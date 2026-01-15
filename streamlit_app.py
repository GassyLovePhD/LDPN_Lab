import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import io
import zipfile

from analysis.loader import load_experiment_data
from analysis.count import compute_droplet_counts
from analysis.plotting import plot_all_graphs
from analysis.count import normalize_to_control
from analysis.count import sort_droplet_counts
from analysis.count import normalize_to_control_extra_for_graphing
from analysis.processing import safe_extract


st.set_page_config(layout="wide")
st.title("Droplet Analysis Tool")
st.sidebar.header("Input Parameters")


input_folder = st.sidebar.text_input("Experiment folder path", placeholder="path/to/your/data")
zip_file = st.sidebar.file_uploader("Upload dataset (.zip)", type=["zip"])
if zip_file:
    with zipfile.ZipFile(zip_file) as zip_ref:
        safe_extract(zip_ref, "uploaded_data")
        members = zip_ref.namelist()
        progress = st.sidebar.progress(0)

        for i, member in enumerate(members):
            zip_ref.extract(member, "uploaded_data")
            progress.progress((i + 1) / len(members))

    st.sidebar.success("Extraction complete!")

csv_file_name = st.sidebar.text_input("CSV file name", placeholder="GFP_Filtered_Droplets.csv")
run_button = st.sidebar.button("Run Analysis")

# -*-*-*- Main Application Logic -*-*-*-
if run_button:
    if not input_folder or not os.path.isdir(input_folder):
        st.error("Please provide a valid experiment folder path.")
        st.stop()

    with st.spinner("Loading data..."):
        all_data = load_experiment_data(input_folder=input_folder, csv_file_name=csv_file_name)
        if all_data.empty:
            st.error("No data found in the specified folder structure.")
            st.stop()
        st.success("Data loaded successfully.")
        st.success(f"Total rows loaded: {len(all_data)}")
        st.subheader("Combined raw data example")
        st.dataframe(all_data.head())

# -*-*-* Compute Droplet Counts -*-*-*-
    with st.spinner("Computing droplet counts..."):
        droplet_counts_df = compute_droplet_counts(all_data)
        droplet_counts_df = normalize_to_control(droplet_counts_df)
        droplet_counts_df = normalize_to_control_extra_for_graphing(droplet_counts_df)
        droplet_counts_df = sort_droplet_counts(droplet_counts_df)
        st.success("Droplet counts computed successfully.")
        st.subheader("Droplet Counts Summary")
        st.dataframe(droplet_counts_df)

# -*-*-* Plotting Results -*-*-*-
    with st.spinner("Generating plots..."):
        st.subheader("Droplet Analysis Plots")
        fig = plot_all_graphs(droplet_counts_df)
        st.pyplot(fig, use_container_width=True)
        buf_pdf = io.BytesIO()
        fig.savefig(buf_pdf, format="pdf", bbox_inches="tight", dpi=300)
        buf_pdf.seek(0)
        buf_png = io.BytesIO()
        fig.savefig(buf_png, format="png", bbox_inches="tight", dpi=300)
        buf_png.seek(0)
        plt.close(fig)
        st.success("Plots generated successfully.")      

# -*-*-* Downloads -*-*-*-
    if all_data is not None and droplet_counts_df is not None:
        st.subheader("Download Results")
        st.download_button(
            "Download combined data CSV",
            all_data.to_csv(index=False).encode('utf-8'),
            file_name='combined_experiment_data.csv',
            mime='text/csv'
        )

        st.download_button(
            "Download droplet counts CSV",
            droplet_counts_df.to_csv(index=False).encode('utf-8'),
            file_name='droplet_counts_summary.csv',
            mime='text/csv'
        )

        st.download_button(
            "Download plots as PDF",
            buf_pdf,
            file_name='droplet_analysis_plots.pdf',
            mime='application/pdf'
        )

        st.download_button(
            "Download plots as PNG",
            buf_png,
            file_name='droplet_analysis_plots.png',
            mime='image/png'
        )

    else:
        st.info("Run the analysis to enable downloads. Ensure valid input folder and CSV file name are provided.")