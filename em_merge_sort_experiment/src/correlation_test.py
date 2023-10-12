"""
Module to test for linear relationship between measured and expected run times, 
i.e., to test for Theta/O(f(n)) scaling behaviour
"""
import math
import pandas as pd
from scipy.stats import pearsonr

RESULTS_PATH = "../res/results_scaling_start.txt"
ALPHA = 0.05

# Begin with loading the data
df = pd.read_csv(RESULTS_PATH, delimiter=",", header=None, engine="python", skiprows=1)
df.columns = [
    "file_seed",
    "Input_Size",
    "Block_Size",
    "N_MB",
    "Block_Size_MB",
    "External_Wall_Clock_Time",
    "External_CPU_Time",
    "Classical_Wall_Clock_Time",
    "Classical_CPU_Time",
    "Merge_Rounds",
    "Classical_Rounds",
    "Sort_Option",
    "Host_Name",
]

# Process columns (except Host_Name and Sort_Option)
for column in df.columns:
    if column not in ("Host_Name", "Sort_Option"):
        df[column] = df[column].apply(
            lambda x: float(x.strip(" MB,").replace(",", ""))
            if isinstance(x, str)
            else x
        )

block_sizes = df["Block_Size_MB"].unique()
input_sizes = sorted(df["Input_Size"].unique())
with open("../res/results_correlation_powers.txt", "w") as file:
    for block_size in block_sizes[:-1]:
        df_host = df[df["Block_Size_MB"] == block_size]
        print(len(df_host))
        observed_times = list(df_host["External_Wall_Clock_Time"])[::-1]
        for power in range(0, 20):
            n_log_n = [
                (n / 100000) ** power * math.log(n / 100000) for n in input_sizes
            ]

            correlation, p_value = pearsonr(observed_times, n_log_n)
            file.write(f"{block_size}, {power}, {correlation}, {p_value}\n")

            if p_value < ALPHA:
                print(
                    f"Block Size {block_size}: Reject null hypothesis (p={p_value}, r={correlation}). \
                        It is unlikely that there is no significant correlation between \
                        the run times and n log n."
                )
            else:
                print(
                    f"Block Size {block_size}: Fail to reject null hypothesis (p={p_value}, r={correlation}). \
                        No significant correlation."
                )
