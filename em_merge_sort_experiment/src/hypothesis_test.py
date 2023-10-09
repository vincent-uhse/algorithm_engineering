import pandas as pd
from scipy.stats import ttest_ind
import numpy as np

results_to_analyze = "../res/results_block_size_analysis.txt"

df = pd.read_csv(
    results_to_analyze, delimiter=",", header=None, engine="python", skiprows=1
)
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

for metric in ["Classical_Wall_Clock_Time", "External_Wall_Clock_Time"]:
    print("Global analysis on metric: " + metric)
    for i in range(len(block_sizes)):
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
        for i in range(len(block_sizes)):
            for j in range(i + 1, len(block_sizes)):
                block_size_1 = block_sizes[i]
                block_size_2 = block_sizes[j]

                data1 = df[
                    (df["Block_Size"] == block_size_1) & (df["file_seed"] == file_seed)
                ][metric]
                data2 = df[
                    (df["Block_Size"] == block_size_2) & (df["file_seed"] == file_seed)
                ][metric]

                t_statistic, p_value = ttest_ind(data1, data2)

                mean_diff = data1.mean() - data2.mean()
                pooled_std_dev = np.sqrt((data1.var() + data2.var()) / 2)
                cohen_d = mean_diff / pooled_std_dev

                print(
                    f"T-test for File Seed {file_seed}, Block Size {block_size_1} vs Block Size {block_size_2}:"
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
                            "File_Seed": f"{file_seed}",
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
                            "File_Seed": f"{file_seed}",
                            "Result": "Not Reject",
                            "p-value": p_value,
                            "cohen_d": cohen_d,
                        }
                    )
        print()


import matplotlib.pyplot as plt
import seaborn as sns


def get_rejection_counts(test_results, metric):
    reject_count = sum(
        1
        for test in test_results
        if test["Result"] == "Reject"
        and test["Metric"] == metric
        and test["File_Seed"] != "Global"
    )
    return len(test_results) - reject_count, reject_count


def plot_bar_chart(categories, counts, title):
    plt.bar(categories, counts, color=["red", "green"])
    plt.xlabel("Test Result")
    plt.ylabel("Frequency")
    plt.title(title)
    plt.savefig(
        f"../vis/hypothesis_test_results/{title.replace(' ', '_')}.pdf", format="pdf"
    )
    plt.close()


def plot_kde(data, title, xlabel, vlines=[]):
    plt.figure(figsize=(8, 6))
    sns.histplot(data, kde=True, color="blue", bins=20)
    plt.xlabel(xlabel)
    plt.ylabel("Density")
    plt.title(title)
    for line in vlines:
        plt.axvline(
            x=line, color="orange", linestyle="--", linewidth=0.8
        )  # Add vertical lines
    plt.savefig(
        f"../vis/hypothesis_test_results/{title.replace(' ', '_')}.pdf", format="pdf"
    )
    plt.close()


# Extract unique block sizes and metrics
comparisons = set()
metrics = set()

for test in hypothesis_test_results:
    block_size_comparison = test.get("Comparison")
    if block_size_comparison:
        comparisons.add(block_size_comparison)
    metric = test.get("Metric")
    if metric:
        metrics.add(test.get("Metric"))

comparisons = sorted(list(comparisons))
metrics = sorted(list(metrics))

for metric in metrics:
    # 1. Get Global Rejection Counts
    not_reject_global, reject_global = get_rejection_counts(
        hypothesis_test_results, metric
    )
    categories_global = ["Not Reject (Global)", "Reject (Global)"]
    counts_global = [not_reject_global, reject_global]

    # 2. Plot Bar Chart for Global Analysis
    plot_bar_chart(
        categories_global, counts_global, f"T-test Results for {metric} (Global)"
    )

    # Loop through each block size comparison
    for comparison in comparisons:
        # Filter test results for the specific block size comparison and metric
        block_size_comparison_results = [
            test
            for test in hypothesis_test_results
            if test.get("Comparison") == comparison and test.get("Metric") == metric
        ]
        print(block_size_comparison_results)
        # 3. Get Rejection Counts for Block Size Comparison
        not_reject, reject = get_rejection_counts(block_size_comparison_results, metric)
        categories = [f"Not Reject ({comparison})", f"Reject ({comparison})"]
        counts = [not_reject, reject]
        # 4. Plot Bar Chart for Block Size Comparison
        plot_bar_chart(
            categories, counts, f"T-test Results for {metric} (Block Size {comparison})"
        )
        # Extract p-values and Cohen's d values for this block size comparison and metric
        p_values = [test["p-value"] for test in block_size_comparison_results]
        cohen_d_values = [test["cohen_d"] for test in block_size_comparison_results]
        # 5. Plot KDE for p-values of Block Size Comparison
        plot_kde(
            p_values,
            f"KDE for p-values of {metric} (Block Size {comparison})",
            "p-value",
            vlines=[0.05],
        )
        # 6. Plot KDE for Cohen's d values of Block Size Comparison
        plot_kde(
            cohen_d_values,
            f"KDE for Cohen's d values of {metric} (Block Size {comparison})",
            "Cohen's d",
            vlines=[-0.2, 0.2],
        )

    # Filter test results for the specific metric
    block_size_comparison_results = [
        test for test in hypothesis_test_results if test.get("Metric") == metric
    ]
    # Extract p-values and Cohen's d values for this metric
    p_values = [test["p-value"] for test in block_size_comparison_results]
    cohen_d_values = [test["cohen_d"] for test in block_size_comparison_results]
    # 7. Plot KDE for p-values of All Tests for a metric
    p_values = [test["p-value"] for test in block_size_comparison_results]
    plot_kde(p_values, f"KDE for p-values of {metric}", "p-value", vlines=[0.05])
    # 8. Plot KDE for Cohen's d values of All Tests for a metric
    cohen_d_values = [test["cohen_d"] for test in block_size_comparison_results]
    plot_kde(
        cohen_d_values,
        f"KDE for Cohen's d of {metric}",
        "Cohen's d",
        vlines=[-0.2, 0.2],
    )
