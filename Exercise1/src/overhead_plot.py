"""
This module is for plotting I/O overhad in the run times.
"""
import pandas as pd
import matplotlib.pyplot as plt

RESULTS_PATH = "../res/results_overhead.txt"

df = pd.read_csv(
    RESULTS_PATH, delimiter=",", engine="python", header=None, skiprows="0"
)
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
df["Host_Name"] = (
    df["Host_Name"]
    .str.replace(" ", "")
    .replace({"BookBook-Pro.fritz.box": "Computer1"})
)
df["Host_Name"] = (
    df["Host_Name"].str.replace(" ", "").replace({"ThinkPadT570": "Computer2"})
)
print(df)
# Process columns (except Host_Name)
for column in df.columns:
    if column != "Host_Name":
        df[column] = df[column].apply(
            lambda x: float(x.strip(" MB").replace(",", ""))
            if isinstance(x, str)
            else x
        )


unique_hosts = df["Host_Name"].unique()
colors = ["blue", "red", "green", "purple", "orange"]

plt.figure(figsize=(10, 6))

for i, host in enumerate(unique_hosts):
    host_df = df[df["Host_Name"] == host]
    plt.scatter(
        host_df["Input_MB"],
        host_df["External_Wall_Clock_Time"],
        label=f"Wall Clock Time ({host})",
        color=colors[i],
    )
    plt.scatter(
        host_df["Input_MB"],
        host_df["External_CPU_Time"],
        label=f"CPU Time ({host})",
        color=colors[i],
        marker="x",
    )

plt.xlabel("Input MB")
plt.ylabel("Time (s)")
plt.title("Wall vs CPU Time over Input MB")
plt.legend()

plt.savefig("overhead.pdf", format="pdf")
plt.close()

df["Time_Ratio"] = df["External_Wall_Clock_Time"] / df["External_CPU_Time"]

plt.figure(figsize=(10, 6))

# Scatter plots for Wall Time and CPU Time
for i, host in enumerate(unique_hosts):
    host_df = df[df["Host_Name"] == host]
    plt.scatter(
        host_df["Input_MB"],
        host_df["Time_Ratio"],
        label=f"Overhead ({host})",
        color=colors[i],
    )

plt.xlabel("Input MB")
plt.ylabel("Wall Clock Time / CPU Time")
plt.title("Wall / CPU Time over Input MB")
plt.legend()

# Save the plot as PDF
plt.savefig("overhead_ratio.pdf", format="pdf")
plt.close()
