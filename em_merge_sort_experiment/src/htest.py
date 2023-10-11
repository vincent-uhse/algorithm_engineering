"""Module to perform hypothesis test regarding the block size 
parameter of the External Memory Merge Sort (and Classical Merge Sort)
algorithm"""
import pandas as pd
from scipy.stats import ttest_ind
import numpy as np

RESULTS_PATH = "../res/results_block_size_analysis.txt"

df = pd.read_csv(RESULTS_PATH, delimiter=",", header=None, engine="python", skiprows=1)
df.columns = [
    "file_seed",
    "N",
    "Block_Size",
    "N_MB",
    "Block_Size_MB",
    "External_Wall_Clock_Time",
    "External_CPU_Time",
    "Classical_Wall_Clock_Time",
    "Classical_CPU_Time",
    "Merge_Rounds",
    "Classical_Rounds",
    "Host_Name",
]

# Process columns (except Host_Name)
for column in df.columns:
    if column != "Host_Name":
        df[column] = df[column].apply(
            lambda x: float(x.strip(" MB,").replace(",", ""))
            if isinstance(x, str)
            else x
        )

# Process Host_Name column to remove spaces
df["Host_Name"] = (
    df["Host_Name"].str.replace(" ", "").replace({"BookBook-Pro-2.local": "MacBook"})
)

block_sizes = df["Block_Size"].unique()
file_seeds = df["file_seed"].unique()

hypothesis_test_results = []


def perform_hypothesis_tests():
    """
    Function to perform hypothesis tests to distinguish the effects
    of small changes in the block size parameter for the External Memory
    Merge Sort algorithm
    """
    for metric in ["Classical_Wall_Clock_Time", "External_Wall_Clock_Time"]:
        print("Global analysis on metric: " + metric)
        for _, i in enumerate(block_sizes):
            for j in range(i + 1, len(block_sizes)):
                block_size_1 = block_sizes[i]
                block_size_2 = block_sizes[j]

                data1 = df[df["Block_Size"] == block_size_1][metric]
                data2 = df[df["Block_Size"] == block_size_2][metric]

                t_statistic, p_value = ttest_ind(data1, data2)

                mean_diff = data1.mean() - data2.mean()
                pooled_std_dev = np.sqrt((data1.var() + data2.var()) / 2)
                cohen_d = mean_diff / pooled_std_dev

                print(
                    f"T-test between Block Size {block_size_1} and Block Size {block_size_2}:"
                )
                print(
                    f"T-statistic: {t_statistic}, p-value: {p_value}, Cohen's d: {cohen_d}"
                )
                if p_value < 0.05:
                    print("Reject null hypothesis: There is a significant difference")
                    hypothesis_test_results.append(
                        {
                            "Metric": metric,
                            "Comparison": f"{block_size_1} vs {block_size_2}",
                            "File_Seed": "Global",
                            "Result": "Reject",
                            "p-value": p_value,
                            "cohen_d": cohen_d,
                        }
                    )
                else:
                    print("Fail to reject null hypothesis: No significant difference")
                    hypothesis_test_results.append(
                        {
                            "Metric": metric,
                            "Comparison": f"{block_size_1} vs {block_size_2}",
                            "File_Seed": "Global",
                            "Result": "Not Reject",
                            "p-value": p_value,
                            "cohen_d": cohen_d,
                        }
                    )
        print()

        for file_seed in file_seeds:
            print("File seed: " + str(file_seed) + "\tMetric: " + metric)
            for _, i in enumerate(block_sizes):
                for j in range(i + 1, len(block_sizes)):
                    block_size_1 = block_sizes[i]
                    block_size_2 = block_sizes[j]

                    data1 = df[
                        (df["Block_Size"] == block_size_1)
                        & (df["file_seed"] == file_seed)
                    ][metric]
                    data2 = df[
                        (df["Block_Size"] == block_size_2)
                        & (df["file_seed"] == file_seed)
                    ][metric]

                    t_statistic, p_value = ttest_ind(data1, data2)

                    mean_diff = data1.mean() - data2.mean()
                    pooled_std_dev = np.sqrt((data1.var() + data2.var()) / 2)
                    cohen_d = mean_diff / pooled_std_dev

                    print(
                        f"T-test for File Seed {file_seed}, \
                            Block Size {block_size_1} vs Block Size {block_size_2}:"
                    )
                    print(
                        f"T-statistic: {t_statistic}, p-value: {p_value}, Cohen's d: {cohen_d}"
                    )
                    if p_value < 0.05:
                        print(
                            "Reject null hypothesis: There is a significant difference"
                        )
                        hypothesis_test_results.append(
                            {
                                "Metric": metric,
                                "Comparison": f"{block_size_1} vs {block_size_2}",
                                "File_Seed": f"{file_seed}",
                                "Result": "Reject",
                                "p-value": p_value,
                                "cohen_d": cohen_d,
                            }
                        )
                    else:
                        print(
                            "Fail to reject null hypothesis: No significant difference"
                        )
                        hypothesis_test_results.append(
                            {
                                "Metric": metric,
                                "Comparison": f"{block_size_1} vs {block_size_2}",
                                "File_Seed": f"{file_seed}",
                                "Result": "Not Reject",
                                "p-value": p_value,
                                "cohen_d": cohen_d,
                            }
                        )
            print()
    return hypothesis_test_results
