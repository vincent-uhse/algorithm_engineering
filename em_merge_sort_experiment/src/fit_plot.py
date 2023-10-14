"""
This module is for the visualization of correlation between measured run times and
assumed functions to test how strong the linear relationship of the measured run times
with the assumed functions are when the input size increases. 
We expect to see a peak of the correlation coefficient when the run times lie in 
Theta(assumed function), i.e, scale the same as that function, apart from a scalar
coefficient. 
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import seaborn as sns

# from scipy.stats import probplot


for metric in [
    "External_Wall_Clock_Time",
    "Classical_Wall_Clock_Time",
    "Merge_Rounds",
    "Classical_Rounds",
]:
    for relationship in [
        "Coefficient",
        "Rsquared",
        "Correlation",
    ]:
        df = pd.read_csv(
            f"../res/results_fit_{metric}.txt",
            header=None,
            names=[
                "Block Size",
                "Function",
                "Coefficient",
                "Rsquared",
                "Correlation",
                "p_Value",
                "Residuals",
            ],
        )

        df["Function"] = pd.to_numeric(df["Function"], errors="coerce")
        df[relationship] = pd.to_numeric(df[relationship], errors="coerce")
        df = df.dropna(subset=["Function", relationship])
        df = df.sort_values(by="Function")
        block_sizes = df["Block Size"].unique()

        # Define a list of markers and colors for each block size
        marker_color_mapping = {
            0.04: ("X", "blue"),
            0.4: ("o", "red"),
            4: ("s", "green"),
            40: ("D", "purple"),
        }

        fig, ax = plt.subplots(figsize=(10, 10))
        ALREADY_LABELED = False
        for i, block_size in enumerate(block_sizes):
            df_block = df[df["Block Size"] == block_size]

            max_corr_row = df_block[
                df_block[relationship] == df_block[relationship].max()
            ]

            f = interp1d(df_block["Function"], df_block[relationship], kind="cubic")
            smooth_curve = np.linspace(
                df_block["Function"].min(), df_block["Function"].max(), 1000
            )
            interpolated_values = f(smooth_curve)

            for j, row in df_block.iterrows():
                x = row["Function"]
                y = row[relationship]
                if j == max_corr_row.index[0]:
                    marker, color = marker_color_mapping[block_size]
                    ax.scatter(
                        x,
                        y,
                        color=color,
                        marker=marker,
                        label=f"Max. ({block_size} MB)",
                    )
                else:
                    ax.scatter(x, y, color="blue")

            ax.plot(
                smooth_curve, interpolated_values, label=f"Block Size {block_size} MB"
            )

        ax.set_xlabel("Power $p$")
        ax.set_ylabel(relationship)
        ax.set_title(
            f"{relationship} vs Power $p$ comparing run times with $n^p log(n)$"
        )
        ax.legend()

        plt.tight_layout()

        # plt.show()
        plt.savefig(
            f"../report/res/fit/{relationship}_{metric}.pdf",
            format="pdf",
        )
        plt.close()

        fig, axes = plt.subplots(
            len(block_sizes), 1, figsize=(10, 5 * len(block_sizes))
        )

        for i, block_size in enumerate(block_sizes):
            df_block = df[df["Block Size"] == block_size]

            max_corr_row = df_block[
                df_block[relationship] == df_block[relationship].max()
            ]

            ax = axes[i]

            for j, row in df_block.iterrows():
                residuals = [float(r) for r in row["Residuals"].split(";")]
                ax.hist(
                    residuals, bins=20, alpha=0.5, label=f'Function {row["Function"]}'
                )

            ax.set_xlabel("Residuals")
            ax.set_ylabel("Frequency")
            ax.set_title(f"Histogram of Residuals for Block Size {block_size} MB")
            ax.legend()

        plt.tight_layout()

        plt.savefig(
            f"../report/res/fit/histogram_residuals_{relationship}_{metric}.pdf",
            format="pdf",
        )
        plt.close()
