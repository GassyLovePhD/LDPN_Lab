import pandas as pd
import os
from analysis.processing import clean_and_average

def load_experiment_data(input_folder, folder_structure=None, csv_file_name="GFP_David_Pipeline_Filter_Droplets.csv"):
    if folder_structure is None:
        folder_structure = {
    "Lithium": {
        "CEFO": ['0', '0.008', '0.01', '0.013', '0.018', '0.024', '0.032', '0.042', '0.056', '0.075'],
        "KAN":  ['0', '0.05', '0.084', '0.14', '0.233', '0.389', '0.648', '1.08', '1.8', '3'],
    },
    "Zinc": {
        "CEFO": ['0', '0.008', '0.01', '0.013', '0.018', '0.024', '0.032', '0.042', '0.056', '0.075'],
        "KAN":  ['0', '0.05', '0.084', '0.14', '0.233', '0.389', '0.648', '1.08', '1.8', '3']
    }
}

    all_data = pd.DataFrame()
    for metal, antibiotics in folder_structure.items():
        for antibiotic, concentration_list in antibiotics.items():
            for concentration in concentration_list:
                folder_concentration = 'Control' if concentration == '0' else concentration
                for day in [0, 9]:
                    day_folder = f"Day{day}_{folder_concentration}"
                    file_path = os.path.join(input_folder, metal, antibiotic, day_folder, csv_file_name)
                    if os.path.isfile(file_path):
                        df = pd.read_csv(file_path)
                        df = clean_and_average(df)
                        df['Metal'] = metal
                        df['Antibiotic'] = antibiotic
                        df['Concentration'] = concentration
                        df['Day'] = day
                        all_data = pd.concat([all_data, df], ignore_index=True)
    return all_data
