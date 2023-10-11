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

block_sizes = df["Block_Size"].unique()
input_sizes = df["Input_Size"].unique()
for block_size in block_sizes:
    df_host = df[df["Block_Size"] == block_size]
    print(len(df_host))
    observed_times = df_host["External_Wall_Clock_Time"]
    n_log_n = [n * math.log(n) for n in reversed(input_sizes)]

    correlation, p_value = pearsonr(observed_times, n_log_n)

    if p_value < ALPHA:
        print(
            f"Block Size {block_size}: Reject null hypothesis (p={p_value}). \
                It is unlikely that there is no significant correlation between \
                the run times and n log n."
        )
    else:
        print(
            f"Block Size {block_size}: Fail to reject null hypothesis (p={p_value}). \
                No significant correlation."
        )
