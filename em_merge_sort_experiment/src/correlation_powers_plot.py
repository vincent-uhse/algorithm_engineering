import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

df = pd.read_csv(
    "../res/results_correlation_powers.txt",
    header=None,
    names=["Block Size", "Function", "Correlation", "Value"],
)

df["Function"] = pd.to_numeric(df["Function"], errors="coerce")
df["Correlation"] = pd.to_numeric(df["Correlation"], errors="coerce")
df = df.dropna(subset=["Function", "Correlation"])
df = df.sort_values(by="Function")
block_sizes = df["Block Size"].unique()

# Define a list of markers and colors for each block size
marker_color_mapping = {
    0.4: ("o", "red"),
    4: ("s", "green"),
    40: ("D", "purple"),
}

fig, ax = plt.subplots(figsize=(10, 10))
already_labeled = False
for i, block_size in enumerate(block_sizes):
    df_block = df[df["Block Size"] == block_size]

    max_corr_row = df_block[df_block["Correlation"] == df_block["Correlation"].max()]

    f = interp1d(df_block["Function"], df_block["Correlation"], kind="cubic")
    smooth_curve = np.linspace(
        df_block["Function"].min(), df_block["Function"].max(), 1000
    )
    interpolated_values = f(smooth_curve)

    for j, row in df_block.iterrows():
        x = row["Function"]
        y = row["Correlation"]
        if j == max_corr_row.index[0]:
            marker, color = marker_color_mapping[block_size]
            ax.scatter(
                x,
                y,
                color=color,
                marker=marker,
                label=f"max.corr. {block_size} MB",
            )
        else:
            ax.scatter(x, y, color="blue")

    ax.plot(smooth_curve, interpolated_values, label=f"Block Size {block_size} MB")


ax.set_xlabel("Power $p$")
ax.set_ylabel("Correlation")
ax.set_title("Correlation vs Power $p$ in correlating with $n^p log(n)$")
ax.legend()

plt.tight_layout()

# plt.show()
plt.savefig("../report/res/correlation_n_log_n.pdf", format="pdf")
plt.close()
