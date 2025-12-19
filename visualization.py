import matplotlib.lines as mlines
import matplotlib.pyplot as plt
import pandas as pd

# Load data
df = pd.read_csv("maimai.csv")

# Preprocessing
df["Achv"] = df["Achv"].astype(str).str.replace("%", "", regex=False)
df["Achv"] = pd.to_numeric(df["Achv"], errors="coerce")
df["Chart Constant"] = pd.to_numeric(df["Chart Constant"], errors="coerce")
df = df.dropna(subset=["Achv", "Chart Constant", "Difficulty"])

# Filter and format
df["Difficulty"] = df["Difficulty"].str.title()
target_difficulties = ["Advanced", "Expert", "Master"]
df = df[df["Difficulty"].isin(target_difficulties)]

# Calculate median trend
median_trend = (
    df.groupby("Chart Constant")["Achv"]
    .median()
    .reset_index()
    .sort_values("Chart Constant")
)

# Configuration
COLORS = {
    "Background": "#F3F3EE",
    "Text": "#13343B",
    "Advanced": "#1FB8CD",
    "Expert": "#DB4545",
    "Master": "#2E8B57",
    "Grid": "#D3D3D3",
}
MARKERS = {"Advanced": "s", "Expert": "^", "Master": "d"}

# Plotting
fig, ax = plt.subplots(figsize=(14, 9))
fig.patch.set_facecolor(COLORS["Background"])
ax.set_facecolor(COLORS["Background"])

# Scatter plots
for diff in target_difficulties:
    subset = df[df["Difficulty"] == diff]
    ax.scatter(
        subset["Chart Constant"],
        subset["Achv"],
        c=COLORS[diff],
        marker=MARKERS[diff],
        s=25,
        label=diff,
        edgecolor="none",
        alpha=0.9,
        zorder=3,
    )

# Median line
ax.plot(
    median_trend["Chart Constant"],
    median_trend["Achv"],
    color="black",
    linestyle=":",
    linewidth=2,
    label="Median Achv by Chart Constant",
    zorder=4,
)

# Styling
ax.grid(True, which="major", axis="both", color=COLORS["Grid"], alpha=0.6, zorder=0)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color(COLORS["Grid"])
ax.spines["bottom"].set_color(COLORS["Grid"])

ax.set_title(
    "Achv vs Chart Constant by Difficulty",
    fontsize=24,
    fontweight="bold",
    color=COLORS["Text"],
    pad=40,
)
ax.set_xlabel("Chart Constant", fontsize=16, color=COLORS["Text"], labelpad=20)
ax.set_ylabel("Achv (%)", fontsize=16, color=COLORS["Text"], labelpad=20)
ax.tick_params(axis="both", colors="#555555", labelsize=12)

# Legend
legend_handles = [
    mlines.Line2D(
        [],
        [],
        color=COLORS["Advanced"],
        marker=MARKERS["Advanced"],
        linestyle="None",
        markersize=8,
        label="Advanced",
    ),
    mlines.Line2D(
        [],
        [],
        color=COLORS["Expert"],
        marker=MARKERS["Expert"],
        linestyle="None",
        markersize=8,
        label="Expert",
    ),
    mlines.Line2D(
        [],
        [],
        color=COLORS["Master"],
        marker=MARKERS["Master"],
        linestyle="None",
        markersize=8,
        label="Master",
    ),
    mlines.Line2D(
        [],
        [],
        color="black",
        linestyle=":",
        linewidth=2,
        label="Median Achv by Chart Constant",
    ),
]

legend = ax.legend(
    handles=legend_handles,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.08),
    ncol=4,
    frameon=False,
    fontsize=13,
)
plt.setp(legend.get_texts(), color="#333333")

# Limits
ax.set_ylim(65, 102)
ax.set_xlim(6.5, 13.8)

plt.tight_layout()
plt.show()
