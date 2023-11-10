"""
This module provides functionality to test for linear relationship 
between measured and expected run times, to test for Theta/O(f(n)) 
scaling behaviour.
"""
import math

import pandas as pd
import statsmodels.api as sm
from scipy.stats import pearsonr

RESULTS_PATH = "../res/results_scaling_start.txt"
ALPHA = 0.05

# Begin with loading the data
df = pd.read_csv(RESULTS_PATH, delimiter=",", header=None, engine="python")
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
            lambda x: float(x.strip(" MB")) if isinstance(x, str) else x
        )

block_sizes = df["Block_Size_MB"].unique()
input_sizes = sorted(df["Input_Size"].unique())
for metric in [
    "External_Wall_Clock_Time",
    "Classical_Wall_Clock_Time",
    "Merge_Rounds",
    "Classical_Rounds",
]:
    with open(f"../res/results_fit_{metric}.txt", "w", encoding="utf8") as file:
        for block_size in block_sizes:
            df_host = df[df["Block_Size_MB"] == block_size]
            observed_times = list(df_host[metric])[::-1]
            # Use a range of powers p in n^p * log(n) to show that
            # one specific power provides the best fit
            for power in range(0, 5):
                n_log_n = [
                    (n / 100000) ** power * math.log(n / 100000) for n in input_sizes
                ]
                # Perform the regression analysis:
                # We want to find out the proportion of the variance in the dependent
                # variable "run time" that is predictable from the independent variable
                # which is our model function run time.
                X = sm.add_constant(n_log_n)  # Add a constant for the intercept
                model = sm.OLS(observed_times, X).fit()

                # Extract relevant information from the model
                coef_n_log_n = model.params[1]  # Coefficient of n^p_log_n
                r_squared = model.rsquared  # R-squared value

                # Measure strength of linear relationship
                correlation, p_value = pearsonr(observed_times, n_log_n)

                # Calculate residuals
                residuals = observed_times - model.predict()

                file.write(
                    f"{block_size}, {power}, \
                    {coef_n_log_n}, {r_squared}, \
                    {correlation}, {p_value}, \
                    {';'.join(map(str, residuals))}\n"
                )
