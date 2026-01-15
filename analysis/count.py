from tokenize import group
import pandas as pd
import numpy as np

def compute_droplet_counts(all_data):
    expected_classes = ["Aggregated", "Homogenous", "Negative"]
    droplet_counts = []

    for (metal, antibiotic, concentration, day), group in all_data.groupby(['Metal', 'Antibiotic', 'Concentration', 'Day']):
       for concentration in group["Concentration"].unique():
           subset = group[group["Concentration"] == concentration]
           class_counts = subset['Classify_Class'].value_counts().to_dict()

           for cls in expected_classes:
               if cls not in class_counts:
                   class_counts[cls] = 0
           
           total_counts = sum(class_counts.values())
           pos_counts = class_counts["Aggregated"] + class_counts["Homogenous"]

           pos_percentage = (pos_counts / total_counts * 100) if total_counts > 0 else 0

           percentages = {
               f"{cls}%": (class_counts[cls] / total_counts * 100) if total_counts > 0 else 0 
               for cls in expected_classes}
           droplet_counts.append({
               'Metal': metal,
               'Antibiotic': antibiotic,
               'Concentration': concentration,
               'Day': day,
               **class_counts,
               "All Droplets": total_counts,
               **percentages,
                "Positive%": pos_percentage,
           })

    df_counts = pd.DataFrame(droplet_counts)
    df_counts["Concentration_numeric"] = df_counts["Concentration"].astype(float)
    df_counts = df_counts.sort_values(by=["Metal", "Antibiotic", "Concentration_numeric", "Day"]).reset_index(drop=True)
    return df_counts

def normalize_to_control(df_counts):
    percentage_cols_pos = ["Positive%"]
    percentage_cols = ["Aggregated%", "Homogenous%", "Negative%"]

    for col in percentage_cols:
        df_counts[f"n{col}"] = 0.0
    df_counts["nPositive%"] = 0.0

    for (metal, antibiotic), group in df_counts.groupby(["Metal", "Antibiotic"]):
        ref_row = group[(group["Day"] == 0) & (np.isclose(group["Concentration_numeric"], 0.0))]

        ref_values = ref_row[percentage_cols_pos].iloc[0].values

        for idx in group.index:
            current_values_pos = group.loc[idx, percentage_cols_pos].values
            normalized_values = np.where(ref_values != 0, (current_values_pos / ref_values) * 100, 0)
            n_pos = normalized_values[0]
            df_counts.loc[idx, "nPositive%"] = n_pos

            for col in percentage_cols:
                df_counts.loc[idx, f"n{col}"] = ((n_pos * df_counts.loc[idx, col]) / 100)
    return df_counts

def normalize_to_control_extra_for_graphing(df_counts):
    for col in ["Aggregated%", "Homogenous%"]:
        df_counts[f"{col} of Pos"] = (
            df_counts[col] / df_counts["Positive%"] * 100
        ).where(df_counts["Positive%"] > 0, 0)

    for col in ["Aggregated% of Pos", "Homogenous% of Pos"]:
        df_counts[f"n{col}"] = (
            df_counts[f"{col}"] * df_counts["nPositive%"] / 100
        ).where(df_counts["nPositive%"] > 0, 0)

    
    return df_counts


# old normalization function for reference
""""
def normalize_to_control(df_counts):
    percentage_cols = ["Aggregated%", "Homogenous%", "Negative%"]
    for col in percentage_cols:
        df_counts[f"n{col}"] = 0.0

    for (metal, antibiotic), group in df_counts.groupby(["Metal", "Antibiotic"]):
        ref_row = group[(group["Day"] == 0) & (np.isclose(group["Concentration_numeric"], 0.0))]
    
        ref_values = ref_row[percentage_cols].iloc[0].values
    
        for idx in group.index:
            current_values = group.loc[idx, percentage_cols].values
            normalized_values = np.where(ref_values != 0, (current_values / ref_values) * 100, 0)
            for col, normalized_value in zip(percentage_cols, normalized_values):
                df_counts.loc[idx, f"n{col}"] = normalized_value
    return df_counts
"""

def sort_droplet_counts(df_counts):
    df_counts = df_counts.sort_values(
        by=["Metal", "Antibiotic", "Day", "Concentration_numeric"]
    ).reset_index(drop=True)
    return df_counts