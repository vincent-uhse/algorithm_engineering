"""Used for plotting statistical analyses on hypothesis tests"""
import matplotlib.pyplot as plt
import seaborn as sns
import htest


hypothesis_test_results = htest.perform_hypothesis_tests()


def get_rejection_counts(test_results, test_metric):
    """Function to calculate the number of rejections in a setting with many hypothesis tests"""
    reject_count = sum(
        1
        for test in test_results
        if test["Result"] == "Reject"
        and test["Metric"] == test_metric
        and test["File_Seed"] != "Global"
    )
    return len(test_results) - reject_count, reject_count


def plot_bar_chart(htest_result_categories, title, rejection_counts=None):
    """
    Function to plot a simple bar chart for reject/fail to reject results
    from hypothesis tests
    """
    if rejection_counts is None:
        rejection_counts = []
    plt.bar(htest_result_categories, rejection_counts, color=["red", "green"])
    plt.xlabel("Test Result")
    plt.ylabel("Frequency")
    plt.title(title)
    plt.savefig(
        f"../vis/hypothesis_test_results/{title.replace(' ', '_')}.pdf",
        format="pdf",
    )
    plt.close()


def plot_kde(data, title, xlabel, vlines=None):
    """Function to plot a kernel density estimation"""
    if vlines is None:
        vlines = []
    plt.figure(figsize=(8, 6))
    sns.histplot(data, kde=True, color="blue", bins=20)
    plt.xlabel(xlabel)
    plt.ylabel("Density")
    plt.title(title)
    for line in vlines:
        # Add vertical lines
        plt.axvline(x=line, color="orange", linestyle="--", linewidth=0.8)
    plt.savefig(
        f"../vis/hypothesis_test_results/{title.replace(' ', '_')}.pdf",
        format="pdf",
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
    # Get Global Rejection Counts
    not_reject_global, reject_global = get_rejection_counts(
        hypothesis_test_results, metric
    )
    categories_global = ["Not Reject (Global)", "Reject (Global)"]
    counts_global = [not_reject_global, reject_global]

    # Plot Bar Chart for Global Analysis
    plot_bar_chart(
        categories_global,
        counts_global,
        f"T-test Results for {metric} (Global)",
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
        # Get rejection counts for block size comparison
        not_reject, reject = get_rejection_counts(block_size_comparison_results, metric)
        categories = [f"Not Reject ({comparison})", f"Reject ({comparison})"]
        counts = [not_reject, reject]
        # Plot Bar Chart for Block Size Comparison
        plot_bar_chart(
            categories,
            counts,
            f"T-test Results for {metric} (Block Size {comparison})",
        )
        # Extract p-values and Cohen's d values for this block size comparison and metric
        p_values = [test["p-value"] for test in block_size_comparison_results]
        cohen_d_values = [test["cohen_d"] for test in block_size_comparison_results]
        # Plot KDE for p-values of block size comparison
        plot_kde(
            p_values,
            f"KDE for p-values of {metric} (Block Size {comparison})",
            "p-value",
            vlines=[0.05],
        )
        # Plot KDE for Cohen's d values of block size comparison
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
