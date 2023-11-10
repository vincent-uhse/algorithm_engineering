"""
This modules is for performing hypothesis tests on the normality of the distributions of run times.
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from scipy.stats import shapiro


RESULTS_PATH = "../res/results_block_size_analysis_normality.txt"
# "../res/results_block_size_analysis_normality.txt"
# "../res/results_block_size_analysis.txt"
# "../res/results_normality_runs.txt"

df = pd.read_csv(RESULTS_PATH, delimiter=",", engine="python", skiprows=1)
df.columns = [
    "File_Seed",
    "Input_Size",
    "Block_Size",
    "Input_MB",
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

# Process columns (except Host_Name)
for column in df.columns:
    if column != "Host_Name":
        df[column] = df[column].apply(
            lambda x: float(x.strip(" MB,").replace(",", ""))
            if isinstance(x, str)
            else x
        )


def shapiro_test(group):
    """This function tests data for normality using the Shapiro-Wilk test"""
    _, p_value = shapiro(group)
    return p_value


p_values = df.groupby(["File_Seed", "Input_Size", "Block_Size"])[
    "Classical_Wall_Clock_Time"
].apply(shapiro_test)
p_values = p_values.reset_index()
p_values.columns = ["File_Seed", "Input_Size", "Block_Size", "Shapiro_p_value"]
print(p_values)

file_seeds = df["File_Seed"].unique()
input_sizes = df["Input_Size"].unique()
block_sizes = df["Block_Size"].unique()

# Create QQ plots
for input_size in input_sizes:
    # for file_seed in file_seeds:
    for block_size in block_sizes:
        normality_count = (
            (p_values["Shapiro_p_value"] > 0.05)
            & (p_values["Input_Size"] == input_size)
            & (p_values["Block_Size"] == block_size)
        ).sum()
        print(
            f"Number of Shapiro p-values indicating normality: {normality_count} (input size: {input_size}, block size: {block_size})"
        )
        # fig, ax = plt.subplots(figsize=(6, 6))
        # p_value = p_values[
        #    (p_values["File_Seed"] == file_seed)
        #    & (p_values["Input_Size"] == input_size)
        #    & (p_values["Block_Size"] == block_size)
        # ]
        # if p_value > 0.05:  # Data is approximately normally distributed
        # data_group = df[
        #    (df["File_Seed"] == file_seed)
        #    & (df["Input_Size"] == input_size)
        #    & (df["Block_Size"] == block_size)
        # ]["External_Wall_Clock_Time"]
        # sm.qqplot(data_group)  # , line="45", ax=ax)

        # plt.savefig(
        #     f"qq_plot_file_{file_seed}_input_{input_size}_block_{block_size}.png"
        # )
        # plt.close()
        #    ax.set_title(f"QQ Plot for Input Size {input_size}, Block Size {block_size}")
        # else:  # Data is not normally distributed
        #    ax.set_title(
        #        f"Data is not normally distributed for Input Size {input_size}, Block Size {block_size}"
        #    )

# Data
input_sizes = [10000, 100000, 1000000]
block_sizes = [16383, 16384, 16385]
external_values = [[4, 2, 3], [12, 12, 9], [65, 63, 62]]
external_values = [[el * 0.01 for el in x] for x in external_values]
classical_values = [[21, 14, 16], [16, 27, 30], [50, 52, 59]]
classical_values = [[el * 0.01 for el in x] for x in classical_values]

plt.figure(figsize=(8, 6))

for i, block_size in enumerate(block_sizes):
    plt.plot(
        input_sizes,
        [value[i] for value in external_values],
        label=f"Block Size {block_size}",
    )

plt.xlabel("Input Size")
plt.ylabel("Proportion")
plt.title(
    "Proportion of files on which run times are normally distributed vs Input Size"
)
plt.xscale("log")
plt.legend()
plt.savefig("plot_normality.pdf", format="pdf")
plt.close()


plt.figure(figsize=(8, 6))

for i, block_size in enumerate(block_sizes):
    plt.plot(
        input_sizes,
        [value[i] for value in classical_values],
        label=f"Block Size {block_size}",
    )

plt.xlabel("Input Size")
plt.ylabel("Proportion")
plt.title(
    "Proportion of files on which run times are normally distributed vs Input Size"
)
plt.xscale("log")
plt.legend()
plt.savefig("plot_normality_classical.pdf", format="pdf")
plt.close()
