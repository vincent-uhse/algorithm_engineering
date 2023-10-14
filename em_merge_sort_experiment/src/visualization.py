"""
Module for Python Plotly visualization of algorithm run times
"""
import pandas as pd
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.neighbors import KernelDensity
from matplotlib.colors import rgb2hex
from scipy.stats import zscore


SHOW_SCATTER_ERROR = True
LIMIT_STD_DEV = True
KDE_BANDWIDTH = 0.03
RESULTS_PATH = "../res/results.txt"


def format_number(size):
    """Function to separate three decimal powers with a dot for readability"""
    size = str((int)(size))
    if len(size) <= 3:
        return size
    return format_number(size[:-3]) + "." + size[-3:]


def truncated_kdeplot(input_data, data_label, plot_color):
    """Function to plot the kernel density estimation of input data with a specified color"""
    kde = sns.kdeplot(
        input_data,
        color=plot_color,
        label=data_label,
        warn_singular=False,
    )

    x, _ = kde.get_lines()[0].get_data()

    plt.scatter(
        input_data, np.zeros_like(input_data), color=color, alpha=0.2
    )  # Scatter plot of data points
    plt.xlim(0, max(x))  # Set x-axis limits from 0 to the maximum x value
    return kde


# Begin with loading the data
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

# Process Host_Name column to remove spaces
df["Host_Name"] = (
    df["Host_Name"].str.replace(" ", "").replace({"BookBook-Pro-2.local": "MacBook"})
)

file_seeds = df["file_seed"].unique()

# Add -1 (columns values globality indicator) to plot data from all files in the same visualization
file_seeds = np.append(file_seeds, -1)

host_names = df["Host_Name"].unique()
host_names = np.append(host_names, "-1")

internal_sort_options = df["Sort_Option"].unique()

for sort_option in internal_sort_options:
    df_host_host = df[df["Sort_Option"] == sort_option]
    for host_name in host_names:
        # Select specific or global data
        df_host = df_host_host[df_host_host["Host_Name"] == host_name]
        df_use = df_host if host_name != "-1" else df_host_host
        for file_seed in file_seeds:
            df_file_filtered = (
                df_use[df_use["file_seed"] == file_seed] if file_seed != -1 else df_use
            )

            block_sizes = df_file_filtered["Block_Size"].unique()
            input_sizes = df_file_filtered["N"].unique()

            if LIMIT_STD_DEV:
                # Filter out outliers that have large Z-scores for the relevant metrics' columns
                z_scores_external = zscore(df_file_filtered["External_Wall_Clock_Time"])
                z_scores_classical = zscore(
                    df_file_filtered["Classical_Wall_Clock_Time"]
                )

                # Set limit to 3 standard deviations
                THRESHOLD = 3
                outliers_mask_external = np.abs(z_scores_external) > THRESHOLD
                outliers_mask_classical = np.abs(z_scores_classical) > THRESHOLD

                # Filter out rows with outliers
                df_file_filtered = df_file_filtered[
                    ~(outliers_mask_external | outliers_mask_classical)
                ]

            palette = sns.color_palette("husl", n_colors=len(block_sizes))
            hex_palette = [rgb2hex(color) for color in palette]
            block_size_colors = {
                size: color for size, color in zip(block_sizes, hex_palette)
            }

            # Use medians as a robust performance metric
            medians_ext = (
                df_file_filtered.groupby(["Block_Size", "N"])[
                    "External_Wall_Clock_Time"
                ]
                .median()
                .reset_index()
            )
            medians_class = (
                df_file_filtered.groupby(["Block_Size", "N"])[
                    "Classical_Wall_Clock_Time"
                ]
                .median()
                .reset_index()
            )

            fig = go.Figure()

            # Calculate IQR for External Wall Clock Time
            q1_ext = (
                df_file_filtered.groupby(["Block_Size", "N"])[
                    "External_Wall_Clock_Time"
                ]
                .quantile(0.25)
                .reset_index()
            )
            q3_ext = (
                df_file_filtered.groupby(["Block_Size", "N"])[
                    "External_Wall_Clock_Time"
                ]
                .quantile(0.75)
                .reset_index()
            )
            iqr_ext = q3_ext.merge(
                q1_ext, on=["Block_Size", "N"], suffixes=("_q3", "_q1")
            )
            iqr_ext["IQR"] = (
                iqr_ext["External_Wall_Clock_Time_q3"]
                - iqr_ext["External_Wall_Clock_Time_q1"]
            )

            # Calculate IQR for Classical Wall Clock Time
            q1_class = (
                df_file_filtered.groupby(["Block_Size", "N"])[
                    "Classical_Wall_Clock_Time"
                ]
                .quantile(0.25)
                .reset_index()
            )
            q3_class = (
                df_file_filtered.groupby(["Block_Size", "N"])[
                    "Classical_Wall_Clock_Time"
                ]
                .quantile(0.75)
                .reset_index()
            )
            iqr_class = q3_class.merge(
                q1_class, on=["Block_Size", "N"], suffixes=("_q3", "_q1")
            )
            iqr_class["IQR"] = (
                iqr_class["Classical_Wall_Clock_Time_q3"]
                - iqr_class["Classical_Wall_Clock_Time_q1"]
            )

            # Add scatter traces for Medians with error bars
            for _, row in medians_ext.iterrows():
                block_size = row["Block_Size"]
                median_wall_clock_time = row["External_Wall_Clock_Time"]
                color = block_size_colors[block_size]

                scatter = go.Scatter(
                    x=[row["N"]],
                    y=[median_wall_clock_time],
                    mode="markers",
                    name=f"Block Size {format_number(block_size)} (External) ({host_name})",
                    marker=dict(size=10, color=color),
                    customdata=[format_number(block_size) + "<br>External"],
                )
                fig.add_trace(scatter)

                iqr_row = iqr_ext[
                    (iqr_ext["Block_Size"] == block_size) & (iqr_ext["N"] == row["N"])
                ]
                iqr_value = iqr_row["IQR"].iloc[0]
                scatter_error = go.Scatter(
                    x=[row["N"]],
                    y=[median_wall_clock_time],
                    mode="markers",
                    marker=dict(size=10, color=color),
                    error_y=dict(type="data", array=[iqr_value / 2], visible=True),
                    customdata=[
                        f"Block Size {format_number(block_size)} (External) ({host_name})"
                    ],
                )
                if SHOW_SCATTER_ERROR:
                    fig.add_trace(scatter_error)

            for _, row in medians_class.iterrows():
                block_size = row["Block_Size"]
                median_wall_clock_time = row["Classical_Wall_Clock_Time"]
                color = block_size_colors[block_size]

                scatter = go.Scatter(
                    x=[row["N"]],
                    y=[median_wall_clock_time],
                    mode="markers",
                    name=f"Block Size {format_number(block_size)} (Classical) ({host_name})",
                    marker=dict(size=10, color=color, symbol="square"),
                    customdata=[format_number(block_size) + "*" + "<br>Classical"],
                )
                fig.add_trace(scatter)

                iqr_row = iqr_class[
                    (iqr_class["Block_Size"] == block_size)
                    & (iqr_class["N"] == row["N"])
                ]
                iqr_value = iqr_row["IQR"].iloc[0]
                scatter_error = go.Scatter(
                    x=[row["N"]],
                    y=[median_wall_clock_time],
                    mode="markers",
                    marker=dict(size=10, color=color, symbol="square"),
                    error_y=dict(type="data", array=[iqr_value / 2], visible=True),
                    customdata=[
                        f"Block Size {format_number(block_size)} (Classical) ({host_name})"
                    ],
                )
                if SHOW_SCATTER_ERROR:
                    fig.add_trace(scatter_error)

            # Connect medians with lines
            for block_size in df_file_filtered["Block_Size"].unique():
                for ext_or_class in ["External", "Classical"]:
                    color = block_size_colors[block_size]

                    medians = (
                        medians_ext if ext_or_class == "External" else medians_class
                    )
                    iqr_data = iqr_ext if ext_or_class == "External" else iqr_class

                    filtered_medians = medians[medians["Block_Size"] == block_size]
                    filtered_iqr = iqr_data[iqr_data["Block_Size"] == block_size]

                    x_vals = filtered_medians["N"]
                    y_vals = filtered_medians[f"{ext_or_class}_Wall_Clock_Time"]
                    iqr_value = filtered_iqr["IQR"] / 2

                    fig.add_trace(
                        go.Scatter(
                            x=x_vals,
                            y=y_vals,
                            mode="lines",
                            name=f"Block Size {format_number(block_size)} ({ext_or_class})",
                            line={"color": color, "width": 2},
                        )
                    )

                    # Add error bars
                    for x_val, y_val, error in zip(x_vals, y_vals, iqr_value):
                        fig.add_trace(
                            go.Scatter(
                                x=[x_val, x_val],
                                y=[y_val - error, y_val + error],
                                mode="lines",
                                line={"color": color, "width": 1},
                                showlegend=False,
                                customdata=[
                                    format_number(block_size) + "<br>Classical"
                                ],
                            )
                        )

            # Use a log-log plot so that we can see differences (change scaling)
            fig.update_layout(
                title="Median Wall Clock Time vs. Input Size",
                xaxis_title="Input Size",
                yaxis_title="Median Wall Clock Time",
                xaxis_type="log",
                yaxis_type="log",
            )

            fig.update_traces(
                hovertemplate="Input Size: %{x}<br>"
                + "Median Wall Clock Time: %{y:.6f}<br>"
                + "Block Size: %{customdata}"
            )

            fig.write_html(
                f"../vis/visualization{'_file_seed_' + str(file_seed) if file_seed != -1 else ''} \
                    {'_host_name_' + host_name if host_name != '-1' else ''} \
                    {'_sort_option_' + str(sort_option) if sort_option != '-1' else ''}.html"
            )
            fig.write_image(
                f"../vis/visualization{'_file_seed_' + str(file_seed) if file_seed != -1 else ''} \
                    {'_host_name_' + host_name if host_name != '-1' else ''} \
                    {'_sort_option_' + str(sort_option) if sort_option != '-1' else ''}.png",
                format="png",
            )

            # Kernel density estimation part {

            labels = []
            # Generate KDE plots for each combination
            for (block_size, n, host_name), data in df_file_filtered.groupby(
                ["Block_Size", "N", "Host_Name"]
            ):
                plt.figure(figsize=(8, 6))

                COLOR_EXTERNAL = "blue"
                COLOR_CLASSICAL = "red"

                truncated_kdeplot(
                    input_data=data["Classical_Wall_Clock_Time"],
                    data_label="Classical",
                    plot_color=COLOR_CLASSICAL,
                )
                truncated_kdeplot(
                    input_data=data["External_Wall_Clock_Time"],
                    data_label=f"External with Block Size {format_number(block_size)} \
                        ({(int) (block_size / 250000)} MB)",
                    plot_color=COLOR_EXTERNAL,
                )

                plt.title(
                    f"KDE for Wall Clock Time (Block Size {format_number(block_size)} \
                        ({(int) (block_size / 250000)} MB), Input Size {format_number(n)} \
                        ({(int) (n / 250000)} MB) ({host_name})"
                )
                plt.xlabel("Wall Clock Time")
                plt.ylabel("Density")
                plt.legend()

                plt.savefig(
                    f"../vis/kde_block_size_{block_size}_n_{n} \
                        {'_file_seed_' + str(file_seed) if file_seed != -1 else ''} \
                        {'_sort_option_' + str(sort_option) if sort_option != '-1' else ''}.svg",
                    format="svg",
                )
                plt.close()

            red_palette = sns.color_palette("Reds", n_colors=len(block_sizes))
            blue_palette = sns.color_palette("Blues", n_colors=len(block_sizes))
            hex_red_palette = [rgb2hex(color) for color in red_palette]
            hex_blue_palette = [rgb2hex(color) for color in blue_palette]

            block_size_red_shades = {
                size: color for size, color in zip(block_sizes, hex_red_palette)
            }
            block_size_blue_shades = {
                size: color for size, color in zip(block_sizes, hex_blue_palette)
            }

            def plotly_similar_kde(input_data, data_label, plot_color, host):
                """Function to prepare kernel density estimation traces for use in Plotly"""
                input_data = input_data.dropna()  # Remove NaN values

                if input_data.empty:
                    return None

                kde = KernelDensity(kernel="gaussian", bandwidth=KDE_BANDWIDTH).fit(
                    input_data.values.reshape(-1, 1)
                )
                kde_points = np.linspace(input_data.min(), input_data.max(), 1000)
                kde_values = np.exp(kde.score_samples(kde_points.reshape(-1, 1)))

                kde_trace = go.Scatter(
                    x=kde_points,
                    y=kde_values,
                    mode="lines",
                    name=f"{data_label} ({host})",
                    line={"color": plot_color},
                )

                data_trace = go.Scatter(
                    x=input_data,
                    y=np.zeros_like(input_data),
                    mode="markers",
                    name=f"{data_label} (Data) ({host})",
                    marker={
                        "size": 5,
                        "color": plot_color,
                        "symbol": "circle",
                    },
                )

                return kde_trace, data_trace

            traces = []

            # Generate KDE plots for each combination
            for (block_size, n, host_name), data in df_file_filtered.groupby(
                ["Block_Size", "N", "Host_Name"]
            ):
                colors = {
                    "External_Wall_Clock_Time": block_size_blue_shades[block_size],
                    "Classical_Wall_Clock_Time": block_size_red_shades[block_size],
                }
                labels = {
                    "External_Wall_Clock_Time": "External",
                    "Classical_Wall_Clock_Time": "Classical",
                }

                for mode in [
                    "External_Wall_Clock_Time",
                    "Classical_Wall_Clock_Time",
                ]:
                    color = colors[mode]
                    label = f"Block Size {format_number(block_size)} \
                        ({labels[mode]}), Input Size {format_number(n)}"

                    traces_kde_data = plotly_similar_kde(
                        input_data=data[mode],
                        data_label=label,
                        plot_color=color,
                        host=host_name,
                    )
                    if traces_kde_data is not None:
                        trace_kde, trace_data = traces_kde_data
                        traces.extend([trace_kde, trace_data])

            layout = go.Layout(
                title="KDE for Wall Clock Time",
                xaxis={"title": "Wall Clock Time"},
                yaxis={"title": "Density", "overlaying": "y"},
                legend={"orientation": "h"},
            )

            fig = go.Figure(data=traces, layout=layout)

            fig.write_html(
                f"../vis/kde_plot{'_file_seed_' + str(file_seed) if file_seed != -1 else ''} \
                    {'_sort_option_' + str(sort_option) if sort_option != '-1' else ''}.html"
            )
            fig.write_image(
                f"../vis/kde_plot{'_file_seed_' + str(file_seed) if file_seed != -1 else ''} \
                    {'_sort_option_' + str(sort_option) if sort_option != '-1' else ''}.png",
                format="png",
            )
            # Kernel density estimation part }
