import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse

OUTPUT_DIR = "graphs"


def load_and_prep(path, window=5):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    df = df[df["Name"] == "Aggregated"]
    df["Seconds"] = df["Timestamp"] - df["Timestamp"].iloc[0]

    # Smooth noisy columns with a rolling median
    numeric_cols = df.select_dtypes(include="number").columns.difference(
        ["Timestamp", "Seconds", "User Count"]
    )
    df[numeric_cols] = (
        df[numeric_cols].rolling(window=window, center=True, min_periods=1).median()
    )

    return df


def save_plot(fig, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")


def make_plot(datasets, x_col, y_col, title, ylabel):
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_title(title, fontsize=14)
    ax.set_xlabel("Concurrent Users")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.4)

    for df, label, color, linestyle in datasets:
        if y_col in df.columns:
            ax.plot(df[x_col], df[y_col], label=label, color=color, linestyle=linestyle)

    if ax.get_legend_handles_labels()[0]:
        ax.legend()

    return fig


def plot_comparison(
    file_a, file_b, file_c=None, label_a="LB A", label_b="LB B", label_c="LB C"
):
    raw_datasets = [
        (load_and_prep(file_a), label_a, "steelblue", "solid"),
        (load_and_prep(file_b), label_b, "tomato", "solid"),
    ]
    if file_c:
        raw_datasets.append((load_and_prep(file_c), label_c, "green", "solid"))

    subtitle = " vs ".join(label for _, label, _, _ in raw_datasets)

    percentile_cols = ["50%", "75%", "90%", "95%", "99%", "99.9%", "100%"]

    # Throughput
    fig = make_plot(
        raw_datasets, "User Count", "Requests/s", f"Throughput — {subtitle}", "Req/s"
    )
    save_plot(fig, "throughput.png")

    # Each percentile
    for col in percentile_cols:
        safe_name = col.replace(".", "_").replace("%", "pct")
        fig = make_plot(
            raw_datasets, "User Count", col, f"p{col} Latency — {subtitle}", "ms"
        )
        save_plot(fig, f"latency_{safe_name}.png")

    # Error rate — computed column, handle separately
    error_datasets = []
    for df, label, color, ls in raw_datasets:
        df = df.copy()
        df["Error Rate %"] = (
            df["Failures/s"] / df["Requests/s"].replace(0, float("nan"))
        ) * 100
        error_datasets.append((df, label, color, ls))

    fig = make_plot(
        error_datasets, "User Count", "Error Rate %", f"Error Rate — {subtitle}", "%"
    )
    save_plot(fig, "error_rate.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_a", default="go_stats_history.csv")
    parser.add_argument("file_b", default="nginx_stats_history.csv")
    parser.add_argument("file_c", nargs="?", default=None)
    parser.add_argument("label_a", default="Go")
    parser.add_argument("label_b", default="Nginx")
    parser.add_argument("label_c", nargs="?", default="LB C")
    args = parser.parse_args()
    plot_comparison(
        args.file_a, args.file_b, args.file_c, args.label_a, args.label_b, args.label_c
    )
