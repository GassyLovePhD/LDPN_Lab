import matplotlib.pyplot as plt
import numpy as np

def set_color(label):
    colors = {
        "Aggregated_d0": (50/255, 80/255, 230/255),
        "Aggregated_d9": (90/255, 115/255, 235/255),
        "Homogenous_d0": (240/255, 220/255, 120/255),
        "Homogenous_d9": (190/255, 180/255, 100/255),
        "Negative": (254/255, 199/255, 86/255),
    }
    return colors.get(label, (0.6,0.6,0.6))

def plot_all_graphs(droplet_counts_df):
    dataset_groups = dict(tuple(droplet_counts_df.groupby(["Metal", "Antibiotic"])))
    fig, axes = plt.subplots(2, 2, figsize=(16, 8))
    axes = axes.flatten()
    titles = list(dataset_groups.keys())

    for ax, ((metal, antibiotic), df), title in zip(axes, dataset_groups.items(), titles):
        if df is None or df.empty:
            ax.axis("off")
            continue
        df_sorted = df.sort_values(["Day", "Concentration_numeric"])
        
        concentration_labels = (
            df_sorted[df_sorted["Day"] == 0].sort_values("Concentration_numeric")
            ["Concentration"].astype(float).astype(str).tolist()
        )
        

        day0 = df_sorted[df_sorted["Day"] == 0]
        day9 = df_sorted[df_sorted["Day"] == 9]

        ref_row = df_sorted[(df_sorted["Day"] == 0) & (df_sorted["Concentration_numeric"] == 0.0)].iloc[0] # Reference row for normalization

        agg_d0_values = (day0["Aggregated%"] / ref_row["Aggregated%"] * 100).tolist()
        agg_d9_values = (day9["Aggregated%"] / ref_row["Aggregated%"] * 100).tolist()
        hom_d0_values = (day0["Homogenous%"] / ref_row["Homogenous%"] * 100).tolist()
        hom_d9_values = (day9["Homogenous%"] / ref_row["Homogenous%"] * 100).tolist()

        x = np.arange(len(concentration_labels))
        width = 0.5

        ax.bar(x - width/3 - 0.1, agg_d0_values, width/1.5, color=set_color("Aggregated_d0"), alpha=0.5)
        ax.bar(x - width/3, agg_d9_values, width/1.5, color=set_color("Aggregated_d9"), alpha=0.9)
        ax.bar(x + width/3 + 0.1, hom_d0_values, width/1.5, color=set_color("Homogenous_d0"), alpha=0.9)
        ax.bar(x + width/3, hom_d9_values, width/1.5, color=set_color("Homogenous_d9"), alpha=0.9)

        ax.set_xticks(x)
        ax.set_xticklabels(concentration_labels, size=12)
        ax.set_xlabel("Concentration (µg/mL)", size=10) # 16 for davids computer screen, 10 for macbook
        ax.set_ylabel("Relative % to Control", size=10) # 16 for davids computer screen, 10 for macbook

        ax.grid(axis='y', linestyle="-", alpha=0.3)
        ax.set_title(f"{metal} with {antibiotic}")
    
    fig.subplots_adjust(hspace=2.0, wspace=0.3)
    fig.tight_layout()
    fig.legend(["Day 0 Aggregated", "Day 9 Aggregated", "Day 0 Homogenous", "Day 9 Homogenous"],
           loc='upper right', fontsize=10)
    
    return fig